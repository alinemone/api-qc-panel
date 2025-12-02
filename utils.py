"""
Safe print utility for Windows console
Handles encoding issues with emojis and special characters
"""
import sys


def safe_print(*args, **kwargs):
    """Print with safe encoding handling for Windows console"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII and ignore errors
        message = ' '.join(str(arg) for arg in args)
        try:
            print(message.encode('ascii', 'ignore').decode('ascii'), **kwargs)
        except:
            # Last resort: just don't print
            pass


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to remove non-encodable characters
    This prevents UnicodeEncodeError on Windows console
    """
    error_str = str(error)
    try:
        # Try to encode to ASCII and remove problematic characters
        return error_str.encode('ascii', 'ignore').decode('ascii')
    except:
        # If that fails, return a generic message
        return "Database error occurred"
