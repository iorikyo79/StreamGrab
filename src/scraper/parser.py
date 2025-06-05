from bs4 import BeautifulSoup
# urllib.parse.urlparse is no longer needed here as is_m3u8_url was moved.
import logging

# Configure basic logging - This might be handled by a central logger in a larger app.
# For now, if main.py sets up logging, this module's loggers will inherit that.
# If run standalone, this basicConfig might apply or be overridden.
# Consider using logging.getLogger(__name__) and letting the main app configure handlers.
logger = logging.getLogger(__name__)
# If no handlers are configured by the application, logs might not appear or go to stderr.
# To ensure standalone testability of this module with logging,
# we can add a basic config here if no handlers exist.
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(module)s - %(message)s')

# Module-level selector constants are now removed.
# Selectors will be passed as arguments to extract_media_urls.

def extract_media_urls(driver, page_url: str, video_selector: str, subtitle_selector: str) -> dict:
    """
    Extracts video and subtitle URLs from the HTML content of a page
    using BeautifulSoup.

    Args:
        driver: A Selenium WebDriver instance, assumed to be on the target page.
        page_url: The URL of the page (for context/logging).
        video_selector: CSS selector for the video source element.
        subtitle_selector: CSS selector for the subtitle track element.

    Returns:
        A dictionary containing 'video_url' and 'subtitle_url'.
        Values can be None if not found.
    """
    logger.info(f"Extracting media URLs from: {page_url} using video_selector='{video_selector}' and subtitle_selector='{subtitle_selector}'")
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract video URL
        video_element = soup.select_one(video_selector)
        extracted_video_url = None
        if video_element and video_element.has_attr('src'):
            extracted_video_url = video_element['src']
            # Corrected log call to use global logging, not logger object from previous step
            logging.info(f"Found video source element: {video_element.name}[src='{extracted_video_url[:50]}...']")
            if not extracted_video_url: # Check if src is empty
                logger.warning(f"Video element found, but 'src' attribute is empty for selector '{video_selector}' on {page_url}")
                extracted_video_url = None # Explicitly set to None
        else:
            logger.warning(f"Video source element not found or 'src' attribute missing for selector '{video_selector}' on {page_url}")

        # Extract subtitle URL
        subtitle_element = soup.select_one(subtitle_selector)
        extracted_subtitle_url = None
        attr_name_subtitle = None # To store which attribute was found

        if subtitle_element:
            if subtitle_element.has_attr('src'):
                extracted_subtitle_url = subtitle_element['src']
                attr_name_subtitle = 'src'
            elif subtitle_element.has_attr('href'): # Check href if src is not present
                extracted_subtitle_url = subtitle_element['href']
                attr_name_subtitle = 'href'
            elif subtitle_element.name == 'script' and subtitle_element.get('type') == 'application/json':
                logger.info(f"Found potential subtitle JSON in script tag using selector: {subtitle_selector}")
                # Actual extraction from JSON would need specific logic

            if extracted_subtitle_url is not None: # An attribute (src or href) was found
                if extracted_subtitle_url == "": # If the attribute value is empty
                    logger.warning(f"Subtitle element '{subtitle_element.name}' found, but '{attr_name_subtitle}' attribute is empty for selector '{subtitle_selector}' on {page_url}")
                    extracted_subtitle_url = None # Treat empty string as not found
                else:
                    logger.info(f"Found subtitle: {subtitle_element.name}[{attr_name_subtitle}='{extracted_subtitle_url[:70]}...']")
            elif attr_name_subtitle is None and not (subtitle_element.name == 'script' and subtitle_element.get('type') == 'application/json'):
                logger.warning(f"Subtitle element '{subtitle_element.name}' found by selector '{subtitle_selector}', but no 'src' or 'href' attribute present or recognized.")
        else:
            logger.warning(f"Subtitle element not found for selector '{subtitle_selector}' on {page_url}")

        return {'video_url': extracted_video_url, 'subtitle_url': extracted_subtitle_url}

    except Exception as e:
        logger.error(f"Error during HTML parsing on {page_url}: {e}")
        return {'video_url': None, 'subtitle_url': None}

# is_m3u8_url function has been moved to src/utils/validator.py

if __name__ == '__main__':
    # Ensure logger for __main__ is configured if running standalone for tests
    # This uses the module-level 'logger' instance.
    if not logger.handlers: # Check if the specific 'logger' instance has handlers
        # If main app didn't add handlers to this specific logger, add a basic one for tests.
        # This basicConfig will affect the root logger if 'logger' is not a child or propagate=True.
        # More robust: get a specific logger for tests and add handler only to it.
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s - %(module)s - %(funcName)s - %(message)s')


    logger.info("--- Testing extract_media_urls (Conceptual) ---")

    class MockWebDriver:
        def __init__(self, html_content=""):
            self.page_source = html_content

    # Define mock selectors for testing, as module-level ones are removed.
    # These are simplified for the mock HTML structure.
    MOCK_VIDEO_SELECTOR = "div#video_container > video > source"
    MOCK_SUBTITLE_SELECTOR = "track#subtitle_track_id"

    # Test Case 1: Both video and subtitle elements present
    mock_html_both_found = f"""
    <html><body>
        <div id="video_container">
            <video>
                <source src="http://example.com/real_video.m3u8" />
            </video>
            <video> <!-- Sibling video, should not be picked by basic select_one -->
                 <source src="http://example.com/other_video.mp4" />
            </video>
        </div>
        <track src="http://example.com/english.vtt" id="subtitle_track_id" />
    </body></html>
    """
    driver_both_found = MockWebDriver(mock_html_both_found)
    urls = extract_media_urls(driver_both_found, "http://example.com/page_with_both",
                              video_selector=MOCK_VIDEO_SELECTOR, subtitle_selector=MOCK_SUBTITLE_SELECTOR)
    logger.info(f"Test Case 1 (Both Found): {urls}")
    assert urls['video_url'] == "http://example.com/real_video.m3u8"
    assert urls['subtitle_url'] == "http://example.com/english.vtt"

    # Test Case 2: Video found, subtitle not found
    mock_html_video_only = f"""
    <html><body>
        <div id="video_container">
            <video><source src="http://example.com/video_only.mp4" /></video>
        </div>
        <!-- No subtitle track with the specified ID -->
    </body></html>
    """
    driver_video_only = MockWebDriver(mock_html_video_only)
    urls = extract_media_urls(driver_video_only, "http://example.com/page_with_video_only",
                              video_selector=MOCK_VIDEO_SELECTOR, subtitle_selector=MOCK_SUBTITLE_SELECTOR)
    logger.info(f"Test Case 2 (Video Only): {urls}")
    assert urls['video_url'] == "http://example.com/video_only.mp4"
    assert urls['subtitle_url'] is None

    # Test Case 3: Subtitle found, video not found
    mock_html_subtitle_only = f"""
    <html><body>
        <track src="http://example.com/subs_only.srt" id="subtitle_track_id" />
        <!-- No video element matching MOCK_VIDEO_SELECTOR -->
    </body></html>
    """
    driver_subtitle_only = MockWebDriver(mock_html_subtitle_only)
    urls = extract_media_urls(driver_subtitle_only, "http://example.com/page_with_subtitle_only",
                              video_selector=MOCK_VIDEO_SELECTOR, subtitle_selector=MOCK_SUBTITLE_SELECTOR)
    logger.info(f"Test Case 3 (Subtitle Only): {urls}")
    assert urls['video_url'] is None
    assert urls['subtitle_url'] == "http://example.com/subs_only.srt"

    # Test Case 4: Neither found
    driver_neither_found = MockWebDriver("<html><body><p>Nothing here</p></body></html>")
    urls = extract_media_urls(driver_neither_found, "http://example.com/page_with_nothing",
                              video_selector=MOCK_VIDEO_SELECTOR, subtitle_selector=MOCK_SUBTITLE_SELECTOR)
    logger.info(f"Test Case 4 (Neither Found): {urls}")
    assert urls['video_url'] is None
    assert urls['subtitle_url'] is None

    # Test Case 5: Empty src attributes
    mock_html_empty_src = f"""
    <html><body>
        <div id="video_container">
            <video><source src="" /></video> <!-- Empty src -->
        </div>
        <track src="" id="subtitle_track_id" /> <!-- Empty src -->
    </body></html>
    """
    driver_empty_src = MockWebDriver(mock_html_empty_src)
    urls = extract_media_urls(driver_empty_src, "http://example.com/page_with_empty_src",
                              video_selector=MOCK_VIDEO_SELECTOR, subtitle_selector=MOCK_SUBTITLE_SELECTOR)
    logger.info(f"Test Case 5 (Empty Src): {urls}")
    assert urls['video_url'] is None
    assert urls['subtitle_url'] is None

    logger.info("\nAll parser module tests for extract_media_urls passed.")
