"""
Advanced image preprocessing utilities for OCR.

Includes:
- Quality validation
- Rotation detection and correction
- Contrast enhancement (CLAHE)
- Noise reduction
- Sharpening
- Adaptive thresholding
"""
import cv2
import numpy as np
import pytesseract
import logging
from typing import Tuple
from PIL import Image

logger = logging.getLogger(__name__)


def validate_image_quality(image: np.ndarray) -> Tuple[bool, str]:
    """
    Validate image quality before OCR processing.
    
    Args:
        image: OpenCV image (numpy array)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check image dimensions
    height, width = image.shape[:2]
    
    if width < 100 or height < 100:
        return False, f"Image too small ({width}x{height}). Minimum 100x100 pixels required."
    
    # Check if image is too dark or too bright
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    mean_brightness = np.mean(gray)
    
    if mean_brightness < 30:
        return False, "Image too dark. Please use better lighting."
    
    if mean_brightness > 225:
        return False, "Image too bright/washed out. Please adjust exposure."
    
    # Check contrast
    std_dev = np.std(gray)
    if std_dev < 15:
        return False, "Image has very low contrast. Text may not be readable."
    
    logger.info(f"Image quality: {width}x{height}, brightness={mean_brightness:.1f}, contrast={std_dev:.1f}")
    return True, ""


def detect_rotation(image: np.ndarray) -> float:
    """
    Detect image rotation angle using text orientation.
    
    Args:
        image: Grayscale image
        
    Returns:
        Rotation angle in degrees (0, 90, 180, 270)
    """
    try:
        # Try to detect orientation using Tesseract
        osd = pytesseract.image_to_osd(image)
        
        # Parse rotation angle from OSD output
        for line in osd.split('\n'):
            if 'Rotate:' in line:
                angle = int(line.split(':')[1].strip())
                logger.info(f"Detected rotation: {angle}°")
                return angle
        
        return 0
    except Exception as e:
        logger.warning(f"Could not detect rotation: {e}")
        return 0


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image by specified angle.
    
    Args:
        image: Input image
        angle: Rotation angle in degrees
        
    Returns:
        Rotated image
    """
    if angle == 0:
        return image
    
    # Perform rotation
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    else:
        # For other angles, use affine transformation
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess_for_ocr(image_path: str, detect_rotation_enabled: bool = True) -> np.ndarray:
    """
    Advanced preprocessing pipeline for better OCR accuracy.
    
    Steps:
    1. Load and validate image quality
    2. Detect and correct rotation
    3. Convert to grayscale
    4. Denoise
    5. Enhance contrast (CLAHE)
    6. Sharpen
    7. Adaptive thresholding
    
    Args:
        image_path: Path to image file
        detect_rotation_enabled: Whether to detect and correct rotation
        
    Returns:
        Preprocessed image optimized for OCR
        
    Raises:
        ValueError: If image quality is insufficient
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Validate image quality
    is_valid, error_msg = validate_image_quality(image)
    if not is_valid:
        logger.warning(f"Image quality check failed: {error_msg}")
        # Don't raise error, just log warning and continue
    
    # Detect and correct rotation
    if detect_rotation_enabled:
        try:
            gray_for_rotation = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rotation_angle = detect_rotation(gray_for_rotation)
            if rotation_angle != 0:
                image = rotate_image(image, rotation_angle)
                logger.info(f"Corrected rotation by {rotation_angle}°")
        except Exception as e:
            logger.warning(f"Rotation detection failed, continuing without correction: {e}")
    
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 1. Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # 2. Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)
    
    # 3. Sharpen the image
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(contrast_enhanced, -1, kernel)
    
    # 4. Adaptive thresholding
    binary = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    logger.info("Image preprocessing complete")
    return binary


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Get image width and height.
    
    Args:
        image_path: Path to image
        
    Returns:
        Tuple of (width, height)
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    height, width = image.shape[:2]
    return width, height


def resize_if_needed(image_path: str, max_dimension: int = 3000) -> str:
    """
    Resize image if it's too large (saves processing time).
    
    Args:
        image_path: Path to image
        max_dimension: Maximum width or height
        
    Returns:
        Path to resized image (or original if no resize needed)
    """
    image = cv2.imread(image_path)
    if image is None:
        return image_path
    
    height, width = image.shape[:2]
    
    if width <= max_dimension and height <= max_dimension:
        return image_path
    
    # Calculate new dimensions
    if width > height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))
    
    # Resize
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Save to temp file
    import os
    temp_path = image_path.replace('.', '_resized.')
    cv2.imwrite(temp_path, resized)
    
    logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
    return temp_path
