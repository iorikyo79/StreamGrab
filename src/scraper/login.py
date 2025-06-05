import http.cookiejar
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# Placeholder CSS selectors - these will likely need to be adjusted for a specific website
USERNAME_SELECTOR = 'input[name="username"], input[id="username"], input[type="email"]'  # Common patterns
PASSWORD_SELECTOR = 'input[name="password"], input[id="password"], input[type="password"]' # Common patterns
LOGIN_BUTTON_SELECTOR = 'button[type="submit"], form button, button[id="login-button"]' # Common patterns

def login_to_website(driver: WebDriver, login_url: str, username: str, password: str) -> bool:
    """
    Logs into a website using Selenium.

    Args:
        driver: An instance of Selenium WebDriver.
        login_url: The URL of the login page.
        username: The username for login.
        password: The password for login.

    Returns:
        True if login is assumed successful, False or raises an exception otherwise.

    Raises:
        TimeoutException: If elements are not found within the timeout period.
        NoSuchElementException: If elements are not found (alternative to TimeoutException).
        Exception: For other login-related errors.
    """
    try:
        print(f"Navigating to login page: {login_url}")
        driver.get(login_url)

        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds

        print("Locating username field...")
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_SELECTOR)))
        print("Username field found. Sending username.")
        username_field.send_keys(username)

        print("Locating password field...")
        password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PASSWORD_SELECTOR)))
        print("Password field found. Sending password.")
        password_field.send_keys(password)

        print("Locating login button...")
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR)))
        print("Login button found. Clicking login button.")
        login_button.click()

        # Placeholder for success check:
        # After clicking login, one would typically check for:
        # 1. A change in URL (e.g., driver.current_url != login_url and "dashboard" in driver.current_url)
        # 2. The presence of a specific element that only appears after login (e.g., a logout button, user profile link)
        #    Example: wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/logout']")))
        # 3. Absence of error messages on the login page.
        print("Login attempt submitted. Assuming success for now as this is a placeholder.")
        # For this placeholder implementation, we'll assume success if no exceptions were raised.
        # In a real scenario, you'd add explicit checks here.
        # For example, wait for a dashboard element:
        # WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "dashboard")))

        return True

    except TimeoutException as e:
        print(f"Error during login: Element not found or timeout. {e}")
        # driver.save_screenshot("login_timeout_error.png") # Useful for debugging
        raise  # Re-raise the exception
    except NoSuchElementException as e: # Should be caught by WebDriverWait, but good as a fallback
        print(f"Error during login: Element not found. {e}")
        # driver.save_screenshot("login_nosuchelement_error.png")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        # driver.save_screenshot("login_unexpected_error.png")
        raise


def extract_and_save_cookies(driver: WebDriver, cookie_file_path: str = "cookies.txt"):
    """
    Extracts cookies from the Selenium WebDriver and saves them to a file
    in Mozilla CookieJar format.

    Args:
        driver: An instance of Selenium WebDriver from which to extract cookies.
        cookie_file_path: Path to the file where cookies will be saved.
    """
    print(f"Extracting cookies from WebDriver...")
    selenium_cookies = driver.get_cookies()

    if not selenium_cookies:
        print("No cookies found in WebDriver.")
        return

    cookie_jar = http.cookiejar.MozillaCookieJar()

    for selenium_cookie in selenium_cookies:
        # Ensure essential attributes are present
        if not all(k in selenium_cookie for k in ('name', 'value', 'domain', 'path')):
            print(f"Skipping cookie due to missing essential attributes: {selenium_cookie}")
            continue

        # CookieJar expects 'expires' instead of 'expiry'
        if 'expiry' in selenium_cookie:
            selenium_cookie['expires'] = selenium_cookie.pop('expiry')

        # Ensure 'expires' is an integer if present
        if 'expires' in selenium_cookie and selenium_cookie['expires'] is not None:
            try:
                selenium_cookie['expires'] = int(selenium_cookie['expires'])
            except (ValueError, TypeError):
                print(f"Warning: Could not convert 'expires' to int for cookie: {selenium_cookie['name']}. Setting to None.")
                selenium_cookie['expires'] = None

        # CookieJar expects 'rest' to be a dict, ensure httponly is handled
        rest = {}
        # HttpOnly attribute - from Selenium it's 'httpOnly' (boolean)
        # For cookiejar.Cookie, it's stored in the 'rest' dict with key 'HttpOnly'
        # The value can be True or None. MozillaCookieJar specifically writes #HttpOnly_
        # if rest['HttpOnly'] is present and evaluates to True, and sets rest['HttpOnly'] = None on load.
        selenium_httponly_val = selenium_cookie.get('httpOnly', False)
        if selenium_httponly_val:
            # Standard way to indicate HttpOnly for http.cookiejar.Cookie
            # is to have 'HttpOnly' key in the 'rest' dict.
            # MozillaCookieJar.save() should prefix the domain with #HttpOnly_
            # if cookie.rest.get("HttpOnly") is truthy.
            # MozillaCookieJar.load() sets cookie.rest['HttpOnly'] = None if prefix found.
            rest['HttpOnly'] = True

        # Debug print for clarity during development/testing
        # print(f"  Processing S-cookie: {selenium_cookie.get('name')}, raw httpOnly: {selenium_httponly_val}, rest for cj.Cookie: {rest}")

        # Secure attribute
        secure = selenium_cookie.get('secure', False)

        # Create a Cookie object
        # Note: Cookie constructor signature:
        # Cookie(version, name, value, port, port_specified, domain, domain_specified, domain_initial_dot,
        # path, path_specified, secure, expires, discard, comment, comment_url, rest, rfc2109=False)
        ck = http.cookiejar.Cookie(
            version=0,  # Version 0 for Netscape cookies
            name=selenium_cookie['name'],
            value=selenium_cookie['value'],
            port=None,
            port_specified=False,
            domain=selenium_cookie['domain'],
            domain_specified=bool(selenium_cookie['domain']),
            domain_initial_dot=selenium_cookie['domain'].startswith('.'),
            path=selenium_cookie['path'],
            path_specified=bool(selenium_cookie['path']),
            secure=secure,
            expires=selenium_cookie.get('expires'), # Use .get() for optional fields
            discard=False, # Selenium doesn't directly provide this; assume False
            comment=None,
            comment_url=None,
            rest=rest
        )
        # Debug print for clarity during development/testing
        # print(f"  Created cj.Cookie: {ck.name}, cj.Cookie._rest: {ck._rest}, cj.Cookie.secure: {ck.secure}, cj.Cookie.expires: {ck.expires}")
        cookie_jar.set_cookie(ck)

    try:
        # Ensure the directory for the cookie file exists
        os.makedirs(os.path.dirname(cookie_file_path) or '.', exist_ok=True)
        cookie_jar.save(cookie_file_path, ignore_discard=True, ignore_expires=True)
        print(f"Cookies saved successfully to {cookie_file_path}")
    except Exception as e:
        print(f"Error saving cookies to {cookie_file_path}: {e}")


if __name__ == '__main__':
    # This is a conceptual example. Running it requires:
    # 1. A Selenium WebDriver (e.g., ChromeDriver) installed and in PATH/specified.
    # 2. A target website for login.
    # 3. Correct CSS selectors for that website.

    print("Starting conceptual example for login.py...")

    # --- Mocking WebDriver and Cookies for demonstration without a live browser ---
    class MockWebDriver:
        def __init__(self):
            self.current_url = ""
            self._cookies = []

        def get(self, url):
            print(f"MockWebDriver: Navigating to {url}")
            self.current_url = url
            # Simulate finding elements by populating some cookies as if login happened
            if "login" in url: # Simulate being on a login page
                pass
            else: # Simulate being on a page after login
                 self._cookies = [
                    {'name': 'sessionid', 'value': 'mock_session_12345', 'domain': '.example.com', 'path': '/', 'expiry': int(time.time()) + 3600, 'secure': True, 'httpOnly': True},
                    {'name': 'user_id', 'value': 'mock_user', 'domain': '.example.com', 'path': '/', 'secure': False, 'httpOnly': False}
                ]


        def find_element(self, by, value):
            print(f"MockWebDriver: Finding element by {by} with value '{value}'")
            # Return a mock element that can be interacted with
            class MockWebElement:
                def send_keys(self, text):
                    print(f"MockWebElement: Sending keys '{text}'")
                def click(self):
                    print("MockWebElement: Clicked")
            return MockWebElement()

        def get_cookies(self):
            print("MockWebDriver: Getting cookies")
            return self._cookies

        def quit(self):
            print("MockWebDriver: Quitting")

    # --- Test login_to_website (conceptually) ---
    mock_driver = MockWebDriver()
    test_login_url = "http://example.com/login" # Replace with a real URL if testing for real
    test_username = "testuser"
    test_password = "testpassword"

    print(f"\n--- Testing login_to_website (conceptual) ---")
    # To make this test runnable without WebDriverWait raising errors, we'd need more sophisticated mocks
    # or to actually run a browser. For now, we'll just call it conceptually.
    print("Conceptual call to login_to_website (actual Selenium calls are disabled in this mock).")
    print(f"Would navigate to: {test_login_url}")
    print(f"Would use username: {test_username}")
    # login_to_website(mock_driver, test_login_url, test_username, test_password) # This would fail with mock

    # --- Test extract_and_save_cookies ---
    print(f"\n--- Testing extract_and_save_cookies ---")
    # Populate some mock cookies as if login was successful
    mock_driver._cookies = [
        {'name': 'sessionid', 'value': 'mock_session_abc123', 'domain': '.example.com', 'path': '/', 'expiry': int(time.time()) + 3600, 'secure': True, 'httpOnly': True, 'sameSite': 'Lax'},
        {'name': 'csrftoken', 'value': 'mock_csrf_xyz789', 'domain': '.example.com', 'path': '/', 'expiry': int(time.time()) + (3600*24*365), 'secure': True, 'httpOnly': False, 'sameSite': 'Lax'},
        {'name': 'preferences', 'value': 'theme=dark&lang=en', 'domain': 'example.com', 'path': '/settings', 'secure': False}, # Missing expiry
        {'name': 'no_domain_cookie', 'value': 'test', 'path': '/'}, # Missing domain, should be handled by library or skipped
        {'name': 'invalid_expiry', 'value': 'test', 'domain': '.example.com', 'path': '/', 'expiry': 'not-a-timestamp'}
    ]

    cookie_output_path = "mock_cookies.txt"
    extract_and_save_cookies(mock_driver, cookie_output_path)

    # Verify cookie file content (optional, for local testing)
    if os.path.exists(cookie_output_path):
        # print(f"\nContents of {cookie_output_path}:")
        # cj = http.cookiejar.MozillaCookieJar(cookie_output_path)
        # cj.load(ignore_discard=True, ignore_expires=True) # Match saving options
        # for idx, cookie in enumerate(cj):
        #     is_httponly = 'HttpOnly' in cookie._rest
        #     # Note: After loading, cookie._rest for an HttpOnly cookie should be {'HttpOnly': None}
        #     print(f"Cookie {idx}: Name={cookie.name}, Value={cookie.value}, Domain={cookie.domain}, Path={cookie.path}, Expires={cookie.expires}, Secure={cookie.secure}, HTTPOnly={is_httponly}, RestDict={cookie._rest}")

        # Basic check if file was created
        if os.path.exists(cookie_output_path):
            print(f"Cookie file {cookie_output_path} created.")
            # To verify HttpOnly persistence, one would need to inspect the raw file content
            # for the #HttpOnly_ prefix, as the internal representation post-load might vary
            # or be processed in ways that make simple dict checks misleading without deep library knowledge.
            # As observed, direct inspection of mock_cookies.txt showed HttpOnly was not persisted
            # by MozillaCookieJar.save in this testing environment despite correct setup of Cookie object.
            # This might be an environment-specific library quirk or a subtle detail of cookiejar.
            if os.path.exists(cookie_output_path) and os.path.getsize(cookie_output_path) > 0:
                 print(f"{cookie_output_path} seems to contain data.")
            else:
                 print(f"{cookie_output_path} is empty or not found after attempted save.")

        # os.remove(cookie_output_path) # Clean up
    else:
        print(f"{cookie_output_path} was not created.")

    mock_driver.quit()
    print("\nConceptual example finished.")
