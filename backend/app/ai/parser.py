"""
Parser and validator for LLM-extracted bill data.

This module validates and cleans LLM output to ensure:
- Data conforms to expected schema
- Numbers are properly formatted
- Math is correct (subtotal + tax = total)
- Invalid items are removed
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when bill data validation fails."""
    pass


def validate_bill_data(data: Dict[str, Any], tolerance_percent: float = 2.0) -> Dict[str, Any]:
    """
    Validate and clean LLM-extracted bill data.
    
    Steps:
    1. Validate schema (required fields present)
    2. Coerce numbers to proper types
    3. Remove invalid items
    4. Validate math (subtotal + tax ≈ total)
    5. Auto-correct minor discrepancies
    
    Args:
        data: Raw LLM output
        tolerance_percent: Acceptable math error percentage (default 2%)
        
    Returns:
        Cleaned and validated bill data
        
    Raises:
        ValidationError: If data is invalid and cannot be auto-corrected
    """
    logger.info("Validating bill data")
    
    # Step 1: Validate schema
    _validate_schema(data)
    
    # Step 2: Coerce numbers
    data = _coerce_numbers(data)
    
    # Step 3: Clean items
    data['items'] = _clean_items(data['items'])
    
    if not data['items']:
        raise ValidationError("No valid items found in bill")
    
    # Step 4: Validate and auto-correct math
    data = _validate_math(data, tolerance_percent)
    
    logger.info(f"Validation successful: {len(data['items'])} items, total: {data['total']}")
    
    return data


def _validate_schema(data: Dict[str, Any]) -> None:
    """
    Validate that data has required fields.
    
    Args:
        data: Bill data dictionary
        
    Raises:
        ValidationError: If required fields are missing
    """
    required_fields = ['items', 'subtotal', 'tax', 'total']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data['items'], list):
        raise ValidationError("'items' must be a list")


def _coerce_numbers(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coerce all numeric fields to proper Decimal type.
    
    Handles:
    - String numbers ("12.50" -> 12.50)
    - Integers (12 -> 12.00)
    - Invalid values (set to 0)
    
    Args:
        data: Bill data
        
    Returns:
        Data with coerced numbers
    """
    # Coerce top-level numbers
    for field in ['subtotal', 'tax', 'total']:
        data[field] = _to_decimal(data[field], field)
    
    # Coerce item numbers
    for item in data['items']:
        if 'price' in item:
            item['price'] = _to_decimal(item['price'], 'price')
        if 'quantity' in item:
            item['quantity'] = _to_int(item['quantity'], 'quantity')
    
    return data


def _to_decimal(value: Any, field_name: str) -> Decimal:
    """
    Convert value to Decimal, handling various input types.
    
    Args:
        value: Input value
        field_name: Field name (for logging)
        
    Returns:
        Decimal value
    """
    try:
        # Handle string with currency symbols
        if isinstance(value, str):
            # Remove common currency symbols and whitespace
            value = value.replace('$', '').replace('₹', '').replace(',', '').strip()
        
        decimal_value = Decimal(str(value))
        
        # Round to 2 decimal places
        return decimal_value.quantize(Decimal('0.01'))
        
    except (InvalidOperation, ValueError, TypeError):
        logger.warning(f"Could not convert {field_name}='{value}' to Decimal, using 0")
        return Decimal('0.00')


def _to_int(value: Any, field_name: str) -> int:
    """
    Convert value to integer.
    
    Args:
        value: Input value
        field_name: Field name (for logging)
        
    Returns:
        Integer value
    """
    try:
        return int(float(value))
    except (ValueError, TypeError):
        logger.warning(f"Could not convert {field_name}='{value}' to int, using 1")
        return 1


def _clean_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove invalid items and clean item data.
    
    An item is valid if it has:
    - name (non-empty string)
    - price (positive number)
    - quantity (positive integer, defaults to 1)
    
    Args:
        items: List of item dictionaries
        
    Returns:
        List of valid items
    """
    valid_items = []
    
    for i, item in enumerate(items):
        # Check required fields
        if 'name' not in item or not item['name']:
            logger.warning(f"Item {i} missing name, skipping")
            continue
        
        if 'price' not in item:
            logger.warning(f"Item {i} missing price, skipping")
            continue
        
        # Ensure quantity
        if 'quantity' not in item:
            item['quantity'] = 1
        
        # Validate values
        if item['price'] <= 0:
            logger.warning(f"Item {i} has invalid price {item['price']}, skipping")
            continue
        
        if item['quantity'] <= 0:
            logger.warning(f"Item {i} has invalid quantity {item['quantity']}, skipping")
            continue
        
        # Clean name
        item['name'] = str(item['name']).strip()
        
        valid_items.append(item)
    
    logger.info(f"Cleaned items: {len(valid_items)}/{len(items)} valid")
    
    return valid_items


def _validate_math(data: Dict[str, Any], tolerance_percent: float) -> Dict[str, Any]:
    """
    Validate that subtotal + tax = total (within tolerance).
    
    If discrepancy is within tolerance, auto-correct.
    If discrepancy is too large, raise error.
    
    Args:
        data: Bill data
        tolerance_percent: Acceptable error percentage
        
    Returns:
        Corrected bill data
        
    Raises:
        ValidationError: If math is incorrect beyond tolerance
    """
    subtotal = data['subtotal']
    tax = data['tax']
    total = data['total']
    
    expected_total = subtotal + tax
    difference = abs(expected_total - total)
    
    # Calculate percentage error
    if total > 0:
        error_percent = (difference / total) * 100
    else:
        error_percent = 0 if difference == 0 else 100
    
    logger.debug(f"Math check: {subtotal} + {tax} = {expected_total} (actual: {total})")
    logger.debug(f"Difference: {difference} ({error_percent:.2f}%)")
    
    if error_percent <= tolerance_percent:
        if difference > 0:
            logger.info(f"Auto-correcting total: {total} -> {expected_total} (error: {error_percent:.2f}%)")
            data['total'] = expected_total
        return data
    else:
        raise ValidationError(
            f"Math validation failed: subtotal ({subtotal}) + tax ({tax}) = {expected_total}, "
            f"but total is {total}. Difference: {difference} ({error_percent:.2f}%)"
        )


def calculate_item_subtotal(items: List[Dict[str, Any]]) -> Decimal:
    """
    Calculate subtotal from items.
    
    Args:
        items: List of items with price and quantity
        
    Returns:
        Total of all items
    """
    subtotal = Decimal('0.00')
    
    for item in items:
        price = Decimal(str(item['price']))
        quantity = int(item['quantity'])
        subtotal += price * quantity
    
    return subtotal.quantize(Decimal('0.01'))
