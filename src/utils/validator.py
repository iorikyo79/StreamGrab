import logging
from urllib.parse import urlparse

# It's good practice for utility modules to use a logger,
# possibly a generic one or one configured by the main application.
# If LOGGER from src.utils.logger is used, ensure no circular dependency.
# For simple utils, can use logging.getLogger(__name__)
logger = logging.getLogger(__name__) # This will inherit config from root or main app's logger setup.
# If you need it to work standalone or have specific formatting here:
# from .logger import setup_logger # Assuming logger.py is in the same directory (utils)
# logger = setup_logger(__name__, level=logging.INFO)


def is_m3u8_url(url: str) -> bool:
    """
    Checks if the given URL is likely an M3U8 playlist URL (case-insensitive for extension).

    Args:
        url: The URL string to check.

    Returns:
        True if the URL path ends with '.m3u8', False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed_url = urlparse(url)
        return parsed_url.path.lower().endswith('.m3u8')
    except Exception as e:
        logger.warning(f"Could not parse URL '{url}' during M3U8 check: {e}")
        return False

def is_valid_url(url: str) -> bool:
    """
    Checks if the given URL string is structurally valid.

    A URL is considered valid if it has a scheme (e.g., http, https)
    and a netloc (e.g., example.com).

    Args:
        url: The URL string to check.

    Returns:
        True if the URL appears structurally valid, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme and parsed_url.netloc)
    except Exception as e:
        # Log the exception if parsing itself fails for some reason, though urlparse is robust
        logger.warning(f"Error parsing URL '{url}' during validation: {e}")
        return False

if __name__ == '__main__':
    # Configure a basic logger for standalone testing of this module.
    # This ensures that log messages from the functions are visible during testing,
    # without relying on the main application's logger setup, which can avoid import issues.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Use the module-level logger for test messages.
    # Note: The module-level 'logger = logging.getLogger(__name__)' will use this basicConfig.
    # If it had specific handlers added by setup_logger from elsewhere, those would be used when part of the app.

    logger.info("--- Testing is_m3u8_url ---") # Use the module-level logger directly
    m3u8_test_cases = {
        "http://example.com/stream.m3u8": True,
        "https://example.com/path/to/video.M3U8": True,
        "http://example.com/video.mp4": False,
        "http://example.com/playlist.m3u8?token=123": True,
        "ftp://server/resource.m3u8": True,
        "//example.com/relative_scheme.m3u8": True, # urlparse handles this, path is /relative_scheme.m3u8
        "justafilename.m3u8": True, # urlparse treats this as path; scheme/netloc are empty
        "anotherfilename.M3U8": True,
        None: False,
        "": False,
        "http://example.com/noextension": False,
        "htp://malformed_url_still_parses_path.m3u8": False, # path is '', '.m3u8' is in netloc
        "http://example.com/test.m3u": False,
    }
    for url, expected in m3u8_test_cases.items():
        result = is_m3u8_url(url)
        logger.info(f"M3U8 Test: URL='{url}', Expected={expected}, Got={result}")
        assert result == expected, f"M3U8 Test Failed: URL='{url}', Expected={expected}, Got={result}"

    logger.info("\n--- Testing is_valid_url ---")
    valid_url_test_cases = {
        "http://example.com": True,
        "https://example.com/path?query=value": True,
        "ftp://user:pass@example.com:21/path": True,
        "http://localhost:8000": True,
        "https://192.168.1.1": True,
        "example.com/path": False,  # No scheme
        "/path/only": False,        # No scheme or netloc
        "http:///path-no-netloc": False, # Scheme but no netloc (urlparse makes netloc empty)
        "juststring": False,
        None: False,
        "": False,
        "htp://example.com": True, # 'htp' is a valid scheme format, urlparse accepts it
        "//example.com/path": False, # Scheme-relative URL, scheme is empty by urlparse if not context
    }
    # For scheme-relative, urlparse needs a default scheme to make it complete
    # e.g. urlparse("//example.com/path", scheme="http") would make it valid.
    # The current is_valid_url doesn't provide a default scheme, so "//" is not valid by itself.

    for url, expected in valid_url_test_cases.items():
        result = is_valid_url(url)
        logger.info(f"Valid URL Test: URL='{url}', Expected={expected}, Got={result}")
        assert result == expected, f"Valid URL Test Failed: URL='{url}', Expected={expected}, Got={result}"

    logger.info("\nAll validator tests passed.")
