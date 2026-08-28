import os
import sys
import json
import numpy as np
import cv2
import onnxruntime as ort

# Default model classes
CLASS_NAMES = {
    0: "text_bubble",
    1: "text_free"
}

def get_model_path():
    """Locate the ONNX model file either in PyInstaller bundle, models/ or local folder."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = getattr(sys, '_MEIPASS', root_dir)
    
    candidates = [
        os.path.join(base_dir, "models", "comic-speech-bubble-detector.onnx"),
        os.path.join(base_dir, "comic-speech-bubble-detector.onnx"),
        os.path.join(root_dir, "models", "comic-speech-bubble-detector.onnx"),
        os.path.join(os.getcwd(), "models", "comic-speech-bubble-detector.onnx"),
        os.path.join(os.getcwd(), "comic-speech-bubble-detector.onnx")
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114)):
    """Resize and pad image while preserving aspect ratio (YOLO standard letterbox)."""
    shape = im.shape[:2]  # [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    dw /= 2
    dh /= 2

    if shape[::-1] != new_unpad:
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return im, r, (dw, dh)

class BubbleProcessor:
    def __init__(self, model_path=None):
        self.model_path = model_path or get_model_path()
        self.session = None
        self.active_provider = "Not Loaded"
        self.input_name = None
        self.input_shape = (1, 3, 640, 640)
        self.class_names = CLASS_NAMES

    def load_model(self, log_callback=None):
        if log_callback is None:
            log_callback = print

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"ONNX Model not found at: {self.model_path}")

        # Choose execution providers based on OS with automatic CPU fallback
        available_providers = ort.get_available_providers()
        log_callback(f"Available ONNX providers on this system: {available_providers}")

        providers_to_try = []
        if sys.platform == 'win32':
            if 'DmlExecutionProvider' in available_providers:
                providers_to_try.append('DmlExecutionProvider')
            if 'CUDAExecutionProvider' in available_providers:
                providers_to_try.append('CUDAExecutionProvider')
        elif sys.platform == 'darwin':
            if 'CoreMLExecutionProvider' in available_providers:
                providers_to_try.append('CoreMLExecutionProvider')
        else:
            if 'CUDAExecutionProvider' in available_providers:
                providers_to_try.append('CUDAExecutionProvider')

        # Always add CPU as fallback
        providers_to_try.append('CPUExecutionProvider')

        log_callback(f"Attempting to initialize ONNX session with: {providers_to_try}")
        
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            self.model_path,
            sess_options=session_options,
            providers=providers_to_try
        )
        
        # Determine actual active provider
        active = self.session.get_providers()
        if 'DmlExecutionProvider' in active:
            self.active_provider = "GPU (DirectML)"
        elif 'CoreMLExecutionProvider' in active:
            self.active_provider = "GPU / Neural Engine (CoreML)"
        elif 'CUDAExecutionProvider' in active:
            self.active_provider = "GPU (CUDA)"
        else:
            self.active_provider = "CPU"

        self.input_name = self.session.get_inputs()[0].name
        log_callback(f"Model loaded successfully. Active accelerator: {self.active_provider}")

    def detect(self, img_input, conf_threshold=0.20, iou_threshold=0.45):
        """
        Run inference on an image path or numpy image array.
        Returns list of dicts: [{"class": "text_bubble", "bbox": [x1, y1, x2, y2], "confidence": 0.95}, ...]
        """
        if self.session is None:
            self.load_model()

        if isinstance(img_input, str):
            # Read image supporting unicode paths on Windows
            img_raw = cv2.imdecode(np.fromfile(img_input, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img_raw is None:
                raise ValueError(f"Could not open image file: {img_input}")
        else:
            img_raw = img_input

        orig_h, orig_w = img_raw.shape[:2]

        # 1. Preprocess: letterbox resize
        img_letterbox, ratio, (pad_w, pad_h) = letterbox(img_raw, new_shape=(640, 640))
        
        # Convert BGR to RGB, normalize [0, 1], transpose to (1, 3, 640, 640)
        img_rgb = cv2.cvtColor(img_letterbox, cv2.COLOR_BGR2RGB)
        img_norm = img_rgb.astype(np.float32) / 255.0
        img_tensor = np.transpose(img_norm, (2, 0, 1))[np.newaxis, ...]

        # 2. Inference
        outputs = self.session.run(None, {self.input_name: img_tensor})
        # Output shape is (1, 6, 8400) -> transpose to (8400, 6)
        preds = np.transpose(outputs[0][0], (1, 0))

        boxes = []
        confidences = []
        class_ids = []

        for pred in preds:
            cx, cy, w, h = pred[:4]
            scores = pred[4:]
            class_id = int(np.argmax(scores))
            conf = float(scores[class_id])

            if conf >= conf_threshold:
                # Convert center xywh in 640x640 to top-left xywh in original coordinates
                x1 = (cx - w / 2 - pad_w) / ratio
                y1 = (cy - h / 2 - pad_h) / ratio
                box_w = w / ratio
                box_h = h / ratio

                boxes.append([int(round(x1)), int(round(y1)), int(round(box_w)), int(round(box_h))])
                confidences.append(float(conf))
                class_ids.append(class_id)

        if not boxes:
            return []

        # 3. Non-Maximum Suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, iou_threshold)
        
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                bx, by, bw, bh = boxes[i]
                x1 = max(0, min(orig_w, bx))
                y1 = max(0, min(orig_h, by))
                x2 = max(0, min(orig_w, bx + bw))
                y2 = max(0, min(orig_h, by + bh))
                
                cls_name = self.class_names.get(class_ids[i], f"class_{class_ids[i]}")
                results.append({
                    "class": cls_name,
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(confidences[i], 4)
                })

        return results

    def process_directory(self, directory, save_debug, progress_callback, log_callback, completion_callback):
        try:
            if self.session is None:
                self.load_model(log_callback)

            valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            image_files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in valid_extensions]

            if not image_files:
                log_callback(f"No images found in {directory}")
                completion_callback(False)
                return

            total_files = len(image_files)
            results_dict = {}

            if save_debug:
                debug_dir = os.path.join(directory, "annotated")
                os.makedirs(debug_dir, exist_ok=True)

            for i, filename in enumerate(image_files):
                img_path = os.path.join(directory, filename)
                log_callback(f"Processing ({i+1}/{total_files}): {filename}")

                file_results = self.detect(img_path, conf_threshold=0.20)
                results_dict[filename] = file_results

                if save_debug:
                    img_raw = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                    for item in file_results:
                        x1, y1, x2, y2 = item["bbox"]
                        cv2.rectangle(img_raw, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(img_raw, f"{item['class']} {item['confidence']:.2f}", (x1, max(20, y1 - 5)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    debug_path = os.path.join(debug_dir, filename)
                    cv2.imencode('.jpg', img_raw)[1].tofile(debug_path)

                progress_callback((i + 1) / total_files)

            json_path = os.path.join(directory, "bubbles_coordinates.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=4)

            log_callback(f"Finished processing. JSON saved to: {json_path}")
            completion_callback(True)

        except Exception as e:
            log_callback(f"Error: {str(e)}")
            completion_callback(False)
