import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCREngine:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
    
    def extract_text(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            result = self.ocr.ocr(image, cls=True)
            if not result or not result[0]:
                return []
            
            extracted_data = []
            for line in result[0]:
                try:
                    bbox = line[0]
                    text_info = line[1]
                    text = text_info[0]
                    confidence = float(text_info[1])
                    
                    extracted_data.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })
                except (IndexError, TypeError, ValueError):
                    continue
            
            return extracted_data
        
        except Exception:
            return []
