"""
Phone number validation and formatting using google-libphonenumber
"""
from typing import Optional
from phonenumbers import parse, format_number, PhoneNumberFormat, is_valid_number
from phonenumbers.phonenumberutil import NumberParseException


def is_valid_phone(phone: str, region: str = None) -> bool:
    """
    Validate phone number
    
    Args:
        phone: Phone number string
        region: Country code (default: None, auto-detect from number)
        
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove any whitespace
    phone = phone.strip()
    
    # If phone starts with +, try parsing without region (E.164 format)
    if phone.startswith("+"):
        try:
            parsed = parse(phone, None)  # None means auto-detect from number
            return is_valid_number(parsed)
        except NumberParseException:
            return False
    
    # Otherwise, try with default region (IN for India) or provided region
    try:
        parsed = parse(phone, region or "IN")
        return is_valid_number(parsed)
    except NumberParseException:
        return False


def format_phone_e164(phone: str, region: str = None) -> Optional[str]:
    """
    Format phone number to E.164 format (+91XXXXXXXXXX)
    
    Args:
        phone: Phone number string
        region: Country code (default: None, auto-detect from number)
        
    Returns:
        Formatted phone number or None if invalid
    """
    if not phone or not isinstance(phone, str):
        return None
    
    # Remove any whitespace
    phone = phone.strip()
    
    # If phone starts with +, try parsing without region (E.164 format)
    if phone.startswith("+"):
        try:
            parsed = parse(phone, None)  # None means auto-detect from number
            if not is_valid_number(parsed):
                return None
            return format_number(parsed, PhoneNumberFormat.E164)
        except NumberParseException:
            return None
    
    # Otherwise, try with default region (IN for India) or provided region
    try:
        parsed = parse(phone, region or "IN")
        if not is_valid_number(parsed):
            return None
        return format_number(parsed, PhoneNumberFormat.E164)
    except NumberParseException:
        return None


def format_phone_national(phone: str, region: str = "IN") -> Optional[str]:
    """
    Format phone number to national format (10-digit for India)
    
    Args:
        phone: Phone number string
        region: Country code (default: IN for India)
        
    Returns:
        Formatted phone number or None if invalid
    """
    if not phone or not isinstance(phone, str):
        return None
    
    try:
        parsed = parse(phone, region)
        if not is_valid_number(parsed):
            return None
        return format_number(parsed, PhoneNumberFormat.NATIONAL)
    except NumberParseException:
        return None
