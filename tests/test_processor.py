import unittest
import numpy as np
import cv2
import os
import sys

# Add project root and src directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.processor import BubbleProcessor

class TestBubbleProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = BubbleProcessor()
        self.processor.load_model()
        self.test_img_path = "temp_unit_test.png"

        # Create a synthetic comic page with an ellipse speech bubble
        img = np.full((800, 600, 3), 255, dtype=np.uint8)
        cv2.ellipse(img, (300, 200), (120, 80), 0, 0, 360, (0, 0, 0), 2)
        cv2.putText(img, "TEST BUBBLE", (220, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.imwrite(self.test_img_path, img)

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)

    def test_detection(self):
        results = self.processor.detect(self.test_img_path, conf_threshold=0.1)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Should detect synthetic speech bubble")
        bubble = results[0]
        self.assertIn("bbox", bubble)
        self.assertIn("confidence", bubble)
        self.assertIn("class", bubble)
        self.assertEqual(len(bubble["bbox"]), 4)

if __name__ == "__main__":
    unittest.main()
