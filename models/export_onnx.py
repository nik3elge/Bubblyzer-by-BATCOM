import os
import shutil
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

def export_model():
    print("Downloading/locating YOLO model weights from Hugging Face...")
    # This repository is public, no token is required
    model_path = hf_hub_download(
        repo_id="ogkalu/comic-speech-bubble-detector-yolov8m",
        filename="comic-speech-bubble-detector.pt"
    )
    print(f"Loaded weights from: {model_path}")
    
    print("Loading YOLO model...")
    model = YOLO(model_path)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    onnx_target = os.path.join(output_dir, "comic-speech-bubble-detector.onnx")
    
    print("Exporting model to ONNX format (opset=17, imgsz=640)...")
    exported_path = model.export(format="onnx", imgsz=640, dynamic=False, opset=17)
    print(f"Exported to: {exported_path}")
    
    if os.path.exists(exported_path) and os.path.abspath(exported_path) != os.path.abspath(onnx_target):
        shutil.copyfile(exported_path, onnx_target)
        print(f"Copied model to: {onnx_target}")

if __name__ == "__main__":
    export_model()
