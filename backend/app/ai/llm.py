"""
LLM client for bill data extraction using Groq API.

Groq provides fast inference with generous rate limits.
Supports models like llama-3.1-70b-versatile and mixtral-8x7b.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM processing fails."""
    pass


class LLMClient:
    """
    Client for interacting with Groq API for bill data extraction.
    
    Uses llama-3.1-70b-versatile model for fast, accurate JSON extraction.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq LLM client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not set. "
                "Please set it to your Groq API key from https://console.groq.com/"
            )
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        
        # Use llama-3.3-70b-versatile for best JSON extraction
        self.model = "llama-3.3-70b-versatile"
        
        # Generation config for deterministic output
        self.temperature = 0  # Deterministic
        self.max_tokens = 2048  # Sufficient for bill data
        
        logger.info(f"LLM client initialized with Groq ({self.model})")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_api(self, prompt: str) -> str:
        """
        Call Groq API with retry logic.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Raw LLM response text
            
        Raises:
            LLMError: If API call fails after retries
        """
        try:
            logger.debug(f"Calling Groq API with prompt length: {len(prompt)}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise bill parser that extracts structured data from receipts. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise LLMError("LLM returned empty response")
            
            result = response.choices[0].message.content.strip()
            logger.info(f"LLM response length: {len(result)} characters")
            
            # Log token usage
            if hasattr(response, 'usage'):
                logger.info(f"Tokens used: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
            
            return result
            
        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            raise LLMError(f"API call failed: {str(e)}")
    
    def extract_bill_data(self, ocr_text: str, include_examples: bool = False) -> Dict[str, Any]:
        """
        Extract structured bill data from OCR text.
        
        Args:
            ocr_text: Raw text extracted from bill image
            include_examples: Whether to include example in prompt (ignored for Groq)
            
        Returns:
            Dictionary with keys: items, subtotal, tax, total
            
        Raises:
            LLMError: If extraction fails or output is invalid
        """
        if not ocr_text or len(ocr_text.strip()) < 10:
            raise LLMError("OCR text is too short or empty")
        
        logger.info("Extracting bill data from OCR text")
        
        # Import prompt
        from app.ai.prompts import get_extraction_prompt
        
        # Get prompt
        prompt = get_extraction_prompt(ocr_text, include_examples=False)
        
        # Call LLM
        response_text = self._call_api(prompt)
        
        # Log response length
        logger.info(f"LLM response length: {len(response_text)} characters")
        
        # Parse JSON response
        try:
            # Groq with json_object mode returns clean JSON
            data = json.loads(response_text)
            logger.info("Successfully parsed LLM response as JSON")
            
            # Validate required fields
            required_fields = ['items', 'subtotal', 'tax', 'total']
            for field in required_fields:
                if field not in data:
                    raise LLMError(f"Missing required field: {field}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response was: {response_text[:1000]}")
            raise LLMError(f"LLM returned invalid JSON: {str(e)}")


# Global client instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create global LLM client instance.
    
    Returns:
        LLMClient instance
    """
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


def extract_bill_data(ocr_text: str) -> Dict[str, Any]:
    """
    Extract bill data from OCR text using LLM.
    
    This is a convenience function that uses the global client.
    
    Args:
        ocr_text: Raw OCR text from bill image
        
    Returns:
        Extracted bill data dictionary
        
    Raises:
        LLMError: If extraction fails
    """
    client = get_llm_client()
    return client.extract_bill_data(ocr_text)
