# StreamGrab

This project analyzes the HTML of specific sites to download videos and subtitles.

## Features

- **Automated Login:** Securely logs into websites to access protected content using Selenium.
- **Cookie Management:** Extracts, saves, and utilizes cookies for persistent sessions, enabling access to restricted media.
- **Flexible URL Input:** Process single media page URLs or batch process multiple URLs from a text file.
- **Configurable HTML Parsing:** Employs BeautifulSoup with user-configurable CSS selectors (via `config.json`) to accurately locate and extract direct video and subtitle links from complex HTML structures.
- **Powerful Media Downloading:** Leverages `yt-dlp` to download videos and subtitles.
    - Supports selection of preferred video quality.
    - Allows specification of multiple subtitle languages (e.g., English, Korean).
    - Handles various subtitle formats.
- **External Configuration:** Most operational parameters (credentials, selectors, paths, download options, retry settings) are managed via an external `config.json` file, allowing easy customization without code changes.
- **Command-Line Interface:** Offers a comprehensive CLI to specify URLs, credentials, configuration paths, and override settings for versatile operation.
- **Retry Mechanism:** Includes a configurable retry system to handle transient network issues or page loading errors, enhancing reliability.
- **Headless Browser Operation:** Supports running the browser (Chrome) in headless mode for server-side or automated execution.
- **Logging & Validation:** Provides detailed logging of operations and validates input URLs for robustness.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The script is run from the command line. You must provide either a direct URL to a video page (`--url`) or a file containing a list of URLs (`--url-file`). Login credentials are also required, either via command-line arguments or through the `config.json` file.

### Basic Command:

```bash
python src/main.py --url <video_page_url> --login-id <your_username> --login-pw <your_password>
```

Or, to process multiple URLs from a file:

```bash
python src/main.py --url-file /path/to/your/urls.txt --login-id <your_username> --login-pw <your_password>
```

### Command-Line Arguments:

The script accepts the following command-line arguments. These can be used to override settings defined in `config.json`.

-   `--url URL`: URL of the single video page to process.
-   `--url-file URL_FILE`: Path to a text file containing URLs (one URL per line).
-   `--login-id LOGIN_ID`: Your login ID (username or email).
-   `--login-pw LOGIN_PW`: Your login password.
-   `--config CONFIG_PATH`: Path to the `config.json` file (default: `config.json` in the project root).
-   `--output-dir OUTPUT_DIRECTORY`: Directory where downloaded media will be saved (overrides config).
-   `--subtitle-lang LANGUAGES`: Comma-separated list of preferred subtitle languages (e.g., `en,ko`, `ja`). Overrides config.
-   `--video-quality QUALITY`: Preferred video quality string for `yt-dlp` (e.g., `best`, `1080p`, `720p`). Overrides config.
-   `--cookie-file COOKIE_FILE_PATH`: Path to save and load cookies from (default: `cookies.txt` or as specified in config).
-   `--headless`: Run the Chrome browser in headless mode (no GUI).
-   `--login-url LOGIN_PAGE_URL`: Specific URL for the login page if it's different from the video page's domain.
-   `--max-retries NUMBER`: Maximum number of retries for processing each URL (overrides config).
-   `--retry-delay SECONDS`: Delay in seconds between retries (overrides config).

**Example with more options:**

```bash
python src/main.py \
    --url "http://example.com/video/123" \
    --login-id "myuser" \
    --login-pw "mypassword123" \
    --output-dir "./my_downloads" \
    --subtitle-lang "en,es" \
    --video-quality "1080p" \
    --headless
```

**Note:**
- Ensure you have activated your virtual environment (if you created one) and installed all necessary dependencies from `requirements.txt` before running the script.
- If login ID or password are not provided via CLI, they must be present in the `config.json` file.
- The TODOs in the "Examples" and "Configuration" sections should still be filled out by the user with project-specific details.

## Examples

Below is a conceptual example of how you might use or interact with this project's components.
**Please replace this with a more specific and relevant example for your project.**

```python
# Assuming your project has a module for a specific task, e.g., data processing or web scraping.
# For instance, if you have a scraper component as indicated by your file structure:

# from src.scraper import login # If login is needed and implemented
from src.scraper import parser # Assuming parser.py contains relevant functions

# Example: Using a parsing function (this is a hypothetical example)
# if __name__ == "__main__":
#     # raw_data = "Some data to parse" # Replace with actual data source
#     # parsed_content = parser.parse_data(raw_data) # Replace with actual function and parameters
#     # print("Parsed Content:", parsed_content)
#
#     # Or, if main.py orchestrates everything:
#     print("To see an example, try running the main script as described in the Usage section.")
#     print("You may need to configure settings in src/config/settings.py first.")

# TODO: Provide a clear, runnable example demonstrating your project's core functionality.
# If your project is a library, show how to import and use its functions/classes.
# If it's an application, show a common use case.
```

For detailed examples, please refer to the `src/main.py` script or any specific example scripts you might have.

## Configuration

- Explain how to configure the project (e.g., environment variables, configuration files like `src/config/settings.py`).
- TODO: Detail any necessary configuration steps. For example, if `src/config/settings.py` needs to be modified or if environment variables need to be set.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
