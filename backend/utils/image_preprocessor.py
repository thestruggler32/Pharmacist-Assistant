"""
Enhanced Image Preprocessing for Messy Handwritten Prescriptions
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any
from pathlib import Path
import os


class ImagePreprocessor:
    """
    Enhanced preprocessor for handwritten prescriptions with multiple modes
    """
    
    def __init__(self, handwriting_mode=False):
        """
        Initialize preprocessor
        
        Args:
            handwriting_mode: If True, use aggressive preprocessing for messy handwriting
        """
        self.handwriting_mode = handwriting_mode
        
        # Standard mode parameters
        self.blur_kernel_size = (3, 3)
        self.adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        self.threshold_type = cv2.THRESH_BINARY
        self.block_size = 11
        self.c_constant = 2
        self.dilation_kernel_size = (2, 2)
        self.dilation_iterations = 1
        
        # Handwriting mode parameters (more aggressive)
        if handwriting_mode:
            self.block_size = 15  # Larger block for varying lighting
            self.c_constant = 5   # More aggressive threshold
            self.dilation_kernel_size = (3, 3)  # Thicker text
            self.dilation_iterations = 2
        
        # Quality check thresholds
        self.min_resolution = 500
        self.blur_threshold = 100.0
        self.contrast_threshold = 30.0
    
    def preprocess(self, image_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Main preprocessing pipeline with handwriting mode support
        """
        
        # Load image with fallback
        try:
            # Try loading with OpenCV
            original_image = cv2.imread(image_path)
            
            # Fallback to PIL if OpenCV fails
            if original_image is None:
                print(f"DEBUG: cv2.imread failed for {image_path}, trying PIL fallback...")
                try:
                    from PIL import Image
                    pil_img = Image.open(image_path)
                    original_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                except Exception as e:
                    print(f"DEBUG: PIL fallback also failed: {e}")
                    raise ValueError(f"Cannot read image from {image_path}")
            
            print(f"DEBUG: Preprocessing Input shape: {original_image.shape}")
            
        except Exception as e:
            print(f"ERROR: Failed to load image: {e}")
            raise ValueError(f"Image loading failed: {e}")

        quality_report = {
            "original_size": original_image.shape[:2],
            "warnings": [],
            "quality_score": "good",
            "handwriting_mode": self.handwriting_mode
        }
        
        # Convert to grayscale
        gray_image = self._convert_to_grayscale(original_image)
        
        # Quality checks
        quality_metrics = self._check_image_quality(gray_image)
        quality_report.update(quality_metrics)
        
        if self.handwriting_mode:
            # Aggressive preprocessing for handwriting
            processed = self._preprocess_handwriting(gray_image)
        else:
            # Standard preprocessing
            processed = self._preprocess_standard(gray_image)
        
        print(f"DEBUG: Preprocessing Output shape: {processed.shape}")
        return processed, quality_report
    
    def _preprocess_standard(self, gray_image: np.ndarray) -> np.ndarray:
        """Standard preprocessing pipeline"""
        # Resize 2x
        resized = self._resize_image(gray_image, scale_factor=2.0)
        
        # Gaussian blur
        blurred = cv2.GaussianBlur(resized, self.blur_kernel_size, 0)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            blurred, 255, self.adaptive_method,
            self.threshold_type, self.block_size, self.c_constant
        )
        
        # Morphological dilation
        kernel = np.ones(self.dilation_kernel_size, np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=self.dilation_iterations)
        
        return dilated
    
    def _preprocess_handwriting(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Aggressive preprocessing for messy handwriting
        
        Steps:
        1. Resize 3x (larger for small text)
        2. CLAHE (contrast enhancement)
        3. Bilateral filter (edge-preserving smoothing)
        4. Morphological closing (connect broken strokes)
        5. Deskew (rotation correction)
        6. Adaptive threshold with larger block
        7. Morphological operations (thicken text)
        """
        # Step 1: Resize 3x for small handwriting
        resized = self._resize_image(gray_image, scale_factor=3.0)
        
        # Step 2: CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        # Step 3: Bilateral filter (smoothing while preserving edges)
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Step 4: Morphological closing to connect broken strokes
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel_close)
        
        # Step 5: Deskew (rotation correction)
        deskewed = self._deskew(closed)
        
        # Step 6: Adaptive threshold with larger block size
        binary = cv2.adaptiveThreshold(
            deskewed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Step 7: Morphological dilation to thicken text
        kernel_dilate = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(binary, kernel_dilate, iterations=2)
        
        # Step 8: Remove small noise
        denoised = self._remove_noise(dilated)
        
        return denoised
    
    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Correct image rotation/skew
        
        IMPORTANT: Only corrects small skew angles (±15 degrees max).
        Larger angles are likely misdetections and would incorrectly rotate the image.
        """
        try:
            # Find all non-zero points
            coords = np.column_stack(np.where(image > 0))
            
            # Calculate rotation angle
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                
                # Adjust angle
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                
                # FIX: Limit deskew to ±15 degrees to prevent 90-degree misrotations
                # Large angles are almost always misdetections from minAreaRect
                MAX_DESKEW_ANGLE = 15.0
                if abs(angle) > MAX_DESKEW_ANGLE:
                    print(f"DEBUG: Skipping large deskew angle ({angle:.1f}°), likely misdetection")
                    return image
                
                # Only deskew if angle is significant but not too large
                if abs(angle) > 0.5:
                    print(f"DEBUG: Applying deskew correction of {angle:.1f}°")
                    (h, w) = image.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(
                        image, M, (w, h),
                        flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_REPLICATE
                    )
                    return rotated
        except Exception as e:
            print(f"DEBUG: Deskew error: {e}")
            pass
        
        return image
    
    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove small noise particles"""
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            image, connectivity=8
        )
        
        # Create output image
        output = np.zeros_like(image)
        
        # Keep only components larger than threshold
        min_size = 20  # Minimum component size
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_size:
                output[labels == i] = 255
        
        return output
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale"""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _resize_image(self, image: np.ndarray, scale_factor: float = 2.0) -> np.ndarray:
        """Resize image"""
        height, width = image.shape
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    def _check_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Check image quality"""
        warnings = []
        quality_score = "good"
        
        height, width = image.shape
        
        # Resolution check
        if width < self.min_resolution or height < self.min_resolution:
            warnings.append(f"Low resolution ({width}x{height})")
            quality_score = "poor"
        
        # Blur detection
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        is_blurry = laplacian_var < self.blur_threshold
        
        if is_blurry:
            warnings.append(f"Blurry image (variance: {laplacian_var:.2f})")
            if quality_score != "poor":
                quality_score = "fair"
        
        # Contrast detection
        contrast = image.std()
        is_low_contrast = contrast < self.contrast_threshold
        
        if is_low_contrast:
            warnings.append(f"Low contrast (std: {contrast:.2f})")
            if quality_score != "poor":
                quality_score = "fair"
        
        return {
            "blur_score": float(laplacian_var),
            "contrast_score": float(contrast),
            "is_blurry": is_blurry,
            "is_low_contrast": is_low_contrast,
            "warnings": warnings,
            "quality_score": quality_score
        }
    
    def save_preprocessed_image(self, image: np.ndarray, output_path: str) -> None:
        """Save preprocessed image"""
        cv2.imwrite(output_path, image)


if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("ENHANCED IMAGE PREPROCESSOR TEST")
    print("=" * 70)
    
    # Test with handwriting mode
    test_image = "filled-medical-prescription-isolated-on-260nw-144551783.webp"
    
    if os.path.exists(test_image):
        print(f"\nTesting on: {test_image}")
        
        # Test standard mode
        print("\n[1/2] Standard Mode:")
        preprocessor_std = ImagePreprocessor(handwriting_mode=False)
        processed_std, report_std = preprocessor_std.preprocess(test_image)
        print(f"  Quality: {report_std['quality_score']}")
        preprocessor_std.save_preprocessed_image(processed_std, "output_standard.jpg")
        print(f"  Saved: output_standard.jpg")
        
        # Test handwriting mode
        print("\n[2/2] Handwriting Mode (Aggressive):")
        preprocessor_hw = ImagePreprocessor(handwriting_mode=True)
        processed_hw, report_hw = preprocessor_hw.preprocess(test_image)
        print(f"  Quality: {report_hw['quality_score']}")
        preprocessor_hw.save_preprocessed_image(processed_hw, "output_handwriting.jpg")
        print(f"  Saved: output_handwriting.jpg")
        
        print("\n" + "=" * 70)
    else:
        print(f"\n✗ Test image not found: {test_image}")
