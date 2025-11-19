"""String utility functions for data formatting and validation."""

import re


def to_camel_case(text: str) -> str:
    """
    Convert a string to camelCase.
    
    Examples:
        "bench press" -> "benchPress"
        "Bench Press" -> "benchPress"
        "BENCH_PRESS" -> "benchPress"
        "bench-press" -> "benchPress"
        "bench_press" -> "benchPress"
    """
    if not text:
        return text
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Replace underscores, hyphens, and multiple spaces with single space
    text = re.sub(r'[_\-\s]+', ' ', text)
    
    # Split by spaces
    words = text.split()
    
    if not words:
        return text
    
    # First word is lowercase, rest are capitalized
    camel_case = words[0].lower()
    for word in words[1:]:
        if word:
            camel_case += word.capitalize()
    
    return camel_case


def validate_exercise_name(name: str) -> str:
    """
    Validate and convert exercise name to camelCase.
    
    Args:
        name: The exercise name to validate and convert
        
    Returns:
        The name converted to camelCase
        
    Raises:
        ValueError: If the name is invalid
    """
    if not name or not name.strip():
        raise ValueError("Exercise name cannot be empty")
    
    # Check for valid characters (letters, numbers, spaces, hyphens, and underscores)
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError("Exercise name can only contain letters, numbers, spaces, hyphens, and underscores")
    
    # Convert to camelCase
    camel_name = to_camel_case(name)
    
    # Additional validation after conversion
    if len(camel_name) > 100:
        raise ValueError("Exercise name cannot exceed 100 characters after conversion")
    
    if len(camel_name) < 1:
        raise ValueError("Exercise name must be at least 1 character after conversion")
    
    # Ensure the result is valid camelCase (starts with lowercase letter)
    if not re.match(r'^[a-z][a-zA-Z0-9]*$', camel_name):
        raise ValueError("Exercise name must start with a lowercase letter and contain only alphanumeric characters")
    
    return camel_name

