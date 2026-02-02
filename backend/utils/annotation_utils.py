"""
Utility functions for annotation visualization and bounding box handling
Adapted from Medecoder repository
"""
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

def numpy_to_base64(np_img):
    """Convert numpy image to base64 for frontend display"""
    pil_image = Image.fromarray(np_img).convert('RGB')
    data = BytesIO()
    pil_image.save(data, "JPEG")
    data64 = base64.b64encode(data.getvalue())
    return 'data:image/jpeg;base64,' + data64.decode('utf-8')

def create_annotated_image(image_path, annotations):
    """
    Draw bounding boxes and text on image
    annotations format: [{
        'x': int, 'y': int, 'width': int, 'height': int, 
        'text': str, 'confidence': float
    }]
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    h, w, _ = img.shape
    
    for annotation in annotations:
        x = annotation.get('x', 0)
        y = annotation.get('y', 0)
        width = annotation.get('width', 0)
        height = annotation.get('height', 0)
        text = annotation.get('text', '')
        confidence = annotation.get('confidence', 1.0)
        
        # Color based on confidence: red (low) to green (high)
        color = (0, int(255 * confidence), int(255 * (1 - confidence)))
        
        # Draw rectangle
        cv2.rectangle(img, (x, y), (x + width, y + height), color, 2)
        
        # Add confidence badge
        label = f"{confidence:.0%}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.rectangle(img, (x, y - label_size[1] - 5), (x + label_size[0], y), color, -1)
        cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return numpy_to_base64(img)

def create_digitized_image(image_path, annotations):
    """Create clean digitized version with extracted text"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    h, w, _ = img.shape
    digitized_img = np.zeros([h, w, 3], dtype=np.uint8)
    digitized_img.fill(255)  # White background
    
    for annotation in annotations:
        x = annotation.get('x', 0)
        y = annotation.get('y', 0)
        height = annotation.get('height', 20)
        width = annotation.get('width', 100)
        text = annotation.get('text', '')
        
        # Calculate font scale based on box size
        font_scale = max(0.4, min(1.2, height / 30))
        
        # Draw text
        cv2.putText(
            digitized_img,
            text,
            (x, y + (height // 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )
    
    return numpy_to_base64(digitized_img)

def convert_ocr_to_annotations(ocr_results, image_path):
    """
    Convert OCR results to annotation format
    Handles various OCR output formats
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    height, width, _ = img.shape
    annotations = []
    
    # Handle list of dictionaries (Mistral/Gemini format)
    if isinstance(ocr_results, list):
        for item in ocr_results:
            if isinstance(item, dict):
                # Try to extract bounding box info if available
                bbox = item.get('bbox', item.get('bounding_box'))
                text = item.get('text', item.get('medicine_name', ''))
                confidence = item.get('confidence', 0.8)
                
                if bbox and len(bbox) >= 4:
                    # Normalize if needed (0-1 range to pixels)
                    if all(0 <= v <= 1 for v in bbox[:4]):
                        x, y, w, h = bbox[:4]
                        x, w = int(x * width), int(w * width)
                        y, h = int(y * height), int(h * height)
                    else:
                        x, y, w, h = bbox[:4]
                    
                    annotations.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'text': str(text),
                        'confidence': confidence
                    })
    
    return annotations

def calculate_confidence_from_medicines(medicines):
    """Calculate overall confidence from medicine extraction results"""
    if not medicines:
        return 0.0
    
    confidences = []
    for med in medicines:
        if isinstance(med, dict):
            conf = med.get('confidence', med.get('detection_confidence', 0.5))
            confidences.append(conf)
    
    return round(sum(confidences) / len(confidences), 2) if confidences else 0.5
