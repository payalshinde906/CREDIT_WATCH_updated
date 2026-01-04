"""
Phone number validation and formatting using google-libphonenumber
"""
from typing import Optional
from phonenumbers import parse, format_number, PhoneNumberFormat, is_valid_number
from phonenumbers.phonenumberutil import NumberParseException


def is_valid_phone(phone: str, region: str = "IN") -> bool:
    """
    Validate phone number
    
    Args:
        phone: Phone number string
        region: Country code (default: IN for India)
        
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    try:
        parsed = parse(phone, region)
        return is_valid_number(parsed)
    except NumberParseException:
        return False


def format_phone_e164(phone: str, region: str = "IN") -> Optional[str]:
    """
    Format phone number to E.164 format (+91XXXXXXXXXX)
    
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
