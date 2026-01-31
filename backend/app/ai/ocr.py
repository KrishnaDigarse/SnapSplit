"""
OCR text extraction from bill images using Tesseract.

This module handles:
- Image preprocessing
- Text extraction via Tesseract OCR
- Error handling for failed OCR
"""
import pytesseract
import logging
from typing import Optional
from app.utils.image import preprocess_for_ocr

# Auto-configure Tesseract path on Windows
try:
    from app.ai import tesseract_config
except ImportError:
    pass  # tesseract_config is optional

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Raised when OCR processing fails."""
    pass


def extract_text_from_image(image_path: str, preprocess: bool = True) -> str:
    """
    Extract text from a bill image using Tesseract OCR with multiple strategies.
    
    Tries multiple preprocessing approaches and returns the best result.
    
    Args:
        image_path: Path to the bill image
        preprocess: Whether to preprocess image before OCR (recommended)
        
    Returns:
        Extracted text with line breaks preserved
        
    Raises:
        OCRError: If OCR fails or no text is detected
        FileNotFoundError: If image file doesn't exist
    """
    try:
        logger.info(f"Starting OCR extraction from: {image_path}")
        
        results = []
        
        # Strategy 1: Direct OCR with PSM 6 (assume uniform block of text)
        try:
            logger.debug("Strategy 1: Direct OCR with PSM 6")
            text1 = pytesseract.image_to_string(image_path, lang='eng', config='--psm 6')
            results.append(("direct_psm6", text1.strip()))
            logger.info(f"Strategy 1 extracted {len(text1.strip())} characters")
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Advanced preprocessing with rotation detection
        if preprocess:
            try:
                logger.debug("Strategy 2: Advanced preprocessing with rotation detection")
                processed_image = preprocess_for_ocr(image_path, detect_rotation_enabled=True)
                text2 = pytesseract.image_to_string(processed_image, lang='eng', config='--psm 6')
                results.append(("advanced", text2.strip()))
                logger.info(f"Strategy 2 extracted {len(text2.strip())} characters")
            except Exception as e:
                logger.warning(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Simple preprocessing without rotation
        try:
            logger.debug("Strategy 3: Simple preprocessing without rotation")
            processed_image = preprocess_for_ocr(image_path, detect_rotation_enabled=False)
            text3 = pytesseract.image_to_string(processed_image, lang='eng', config='--psm 6')
            results.append(("simple", text3.strip()))
            logger.info(f"Strategy 3 extracted {len(text3.strip())} characters")
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {e}")
        
        # Strategy 4: Direct OCR with PSM 3 (auto page segmentation)
        try:
            logger.debug("Strategy 4: Direct OCR with PSM 3 (auto page segmentation)")
            text4 = pytesseract.image_to_string(image_path, lang='eng', config='--psm 3')
            results.append(("direct_psm3", text4.strip()))
            logger.info(f"Strategy 4 extracted {len(text4.strip())} characters")
        except Exception as e:
            logger.warning(f"Strategy 4 failed: {e}")
        
        # Find the best result using quality scoring
        if not results:
            raise OCRError("All OCR strategies failed")
        
        # Score each result based on multiple quality indicators
        scored_results = []
        for strategy, text in results:
            if len(text) < 10:
                score = 0  # Too short, likely garbage
            else:
                # Quality indicators:
                # 1. Length (more text is usually better)
                length_score = len(text)
                
                # 2. Word count (more words = more structure)
                word_count = len(text.split())
                
                # 3. Numeric content (bills have numbers)
                digit_count = sum(c.isdigit() for c in text)
                
                # 4. Alphanumeric ratio (too many special chars = garbage)
                alnum_count = sum(c.isalnum() for c in text)
                alnum_ratio = alnum_count / len(text) if len(text) > 0 else 0
                
                # Combined score (weighted)
                score = (
                    length_score * 1.0 +      # Length is important
                    word_count * 5.0 +         # Words indicate structure
                    digit_count * 3.0 +        # Numbers are crucial for bills
                    alnum_ratio * 100.0        # Penalize garbage characters
                )
            
            scored_results.append((score, strategy, text))
            logger.debug(f"{strategy}: score={score:.1f}, len={len(text)}, words={len(text.split())}")
        
        # Pick the highest scoring result
        best_score, best_strategy, best_text = max(scored_results, key=lambda x: x[0])
        
        if not best_text or len(best_text) < 10:
            logger.error(f"Best OCR result too short: {len(best_text)} characters")
            logger.error(f"All results: {[(s, len(t)) for _, s, t in scored_results]}")
            raise OCRError(
                "No text detected in image. Please ensure the image is clear and contains readable text."
            )
        
        logger.info(f"Best strategy: {best_strategy} with score {best_score:.1f} ({len(best_text)} characters)")
        logger.debug(f"OCR text preview: {best_text[:200]}...")
        
        return best_text
        
        
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        raise
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract OCR is not installed or not in PATH")
        raise OCRError(
            "Tesseract OCR is not installed. "
            "Please install it: https://github.com/tesseract-ocr/tesseract"
        )
    except OCRError:
        raise
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise OCRError(f"Failed to extract text from image: {str(e)}")


def validate_ocr_output(text: str, min_length: int = 10) -> bool:
    """
    Validate that OCR output is usable.
    
    Args:
        text: OCR extracted text
        min_length: Minimum acceptable text length
        
    Returns:
        True if text is valid, False otherwise
    """
    if not text or len(text.strip()) < min_length:
        return False
    
    # Check if text contains at least some alphanumeric characters
    alphanumeric_count = sum(c.isalnum() for c in text)
    if alphanumeric_count < min_length:
        return False
    
    return True


def get_ocr_confidence(image_path: str) -> Optional[float]:
    """
    Get OCR confidence score (0-100).
    
    Higher confidence means better OCR quality.
    Useful for deciding whether to proceed with LLM extraction.
    
    Args:
        image_path: Path to image
        
    Returns:
        Average confidence score or None if unavailable
    """
    try:
        processed_image = preprocess_for_ocr(image_path)
        data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence (excluding -1 which means no detection)
        confidences = [int(conf) for conf in data['conf'] if int(conf) != -1]
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            logger.info(f"OCR confidence: {avg_confidence:.2f}%")
            return avg_confidence
        
        return None
        
    except Exception as e:
        logger.warning(f"Could not calculate OCR confidence: {str(e)}")
        return None
