"""
Form Validation Module
Provides validation functions for form inputs.
"""

import re
from typing import Tuple, Callable, Any

def validate_price(action: str, value_if_allowed: str) -> bool:
    """
    Validate price input to ensure it's a valid price format.
    For use with tkinter validatecommand.
    
    Args:
        action: Action code (1=insert, 0=delete, -1=focus, etc.)
        value_if_allowed: New value if edit is allowed
        
    Returns:
        True if input is valid, False otherwise
    """
    # Always allow deletion
    if action != "1":
        return True
    
    # Check for valid price format (digits with optional decimal point and up to 2 decimal places)
    if re.match(r"^\d*\.?\d{0,2}$", value_if_allowed):
        return True
    else:
        return False

def validate_discount(new_value: str) -> bool:
    """
    Validate discount input to ensure it's between
    0-100 (percentage).
    
    Args:
        new_value: Input value to validate
        
    Returns:
        True if input is valid, False otherwise
    """
    if new_value == "":
        return True
    
    try:
        discount_value = float(new_value)
        return 0 <= discount_value <= 100
    except ValueError:
        return False

def validate_integer(action: str, value_if_allowed: str) -> bool:
    """
    Validate integer input.
    For use with tkinter validatecommand.
    
    Args:
        action: Action code (1=insert, 0=delete, -1=focus, etc.)
        value_if_allowed: New value if edit is allowed
        
    Returns:
        True if input is valid, False otherwise
    """
    # Always allow deletion
    if action != "1":
        return True
    
    # Allow empty string
    if value_if_allowed == "":
        return True
    
    # Check if input contains only digits
    return value_if_allowed.isdigit()

def validate_positive_integer(action: str, value_if_allowed: str) -> bool:
    """
    Validate positive integer input (>0).
    For use with tkinter validatecommand.
    
    Args:
        action: Action code (1=insert, 0=delete, -1=focus, etc.)
        value_if_allowed: New value if edit is allowed
        
    Returns:
        True if input is valid, False otherwise
    """
    # Always allow deletion
    if action != "1":
        return True
    
    # Allow empty string
    if value_if_allowed == "":
        return True
    
    # Check if input contains only digits and is greater than 0
    if value_if_allowed.isdigit():
        return int(value_if_allowed) > 0
    return False

def validate_barcode(action: str, value_if_allowed: str) -> bool:
    """
    Validate barcode input (alphanumeric).
    For use with tkinter validatecommand.
    
    Args:
        action: Action code (1=insert, 0=delete, -1=focus, etc.)
        value_if_allowed: New value if edit is allowed
        
    Returns:
        True if input is valid, False otherwise
    """
    # Always allow deletion
    if action != "1":
        return True
    
    # Check if input contains only alphanumeric characters
    return value_if_allowed.isalnum()

def create_validator(root, validator_func: Callable) -> Tuple[Callable, str]:
    """
    Create a Tkinter validator for an entry widget.
    
    Args:
        root: The Tkinter root or parent widget
        validator_func: The validation function to use
        
    Returns:
        Tuple containing the validation command and validation type
    """
    if validator_func == validate_price:
        return (root.register(validator_func), '%d', '%P')
    elif validator_func in (validate_integer, validate_positive_integer, validate_barcode):
        return (root.register(validator_func), '%d', '%P')
    else:
        return (root.register(validator_func), '%P')