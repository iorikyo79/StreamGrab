import argparse
import json
import os
# import logging # Logger will be imported from utils
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config.settings import load_settings
from scraper.login import login_to_website, extract_and_save_cookies
from scraper.parser import extract_media_urls
from downloader.media import download_video_with_subtitles
from utils.logger import LOGGER # Using pre-configured global logger
from utils.validator import is_m3u8_url, is_valid_url

# Retry constants are now fetched from settings or overridden by CLI args.

def main():
    parser = argparse.ArgumentParser(description="Automated media downloader.")
    parser.add_argument("--url", type=str, help="Single video page URL to process.")
    parser.add_argument("--url-file", type=str, help="Path to a file containing multiple URLs (one per line).")
    parser.add_argument("--login-id", type=str, help="Login ID (username/email).")
    parser.add_argument("--login-pw", type=str, help="Login password.")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config.json (default: config.json).")
    parser.add_argument("--output-dir", type=str, help="Directory to save downloaded media.")
    parser.add_argument("--subtitle-lang", type=str, help="Comma-separated subtitle languages (e.g., en,ko).")
    parser.add_argument("--video-quality", type=str, help="Preferred video quality (yt-dlp format string).")
    parser.add_argument("--cookie-file", type=str, help="Path to save and use cookies (default: from config or cookies.txt).")
    parser.add_argument("--headless", action='store_true', help="Run Chrome in headless mode.")
    parser.add_argument("--login-url", type=str, help="Specific URL for the login page, if different from video page.")
    parser.add_argument("--max-retries", type=int, help="Maximum number of retries for processing a URL. Overrides config.")
    parser.add_argument("--retry-delay", type=int, help="Delay in seconds between retries. Overrides config.")

    args = parser.parse_args()

    if not args.url and not args.url_file:
        parser.error("Either --url or --url-file must be provided.")
        sys.exit(1)

    settings = load_settings(args.config)

    # Override settings with command-line arguments
    login_id = args.login_id or settings['login']['username']

    # Password handling with warning
    login_pw_from_cli = bool(args.login_pw)
    login_pw = args.login_pw or settings['login']['password']
    if not login_pw_from_cli and settings['login']['password']:
        if settings['login']['password']:
            LOGGER.warning("Loading password from configuration file. Ensure 'config.json' is secured if it contains sensitive credentials.")
            if isinstance(settings['login']['password'], str) and settings['login']['password'].startswith("ENC["):
                LOGGER.info("Password in config appears to be a placeholder for an encrypted value (e.g., starts with 'ENC['). Actual decryption is not implemented.")

    if not login_id or not login_pw:
        LOGGER.error("Login ID or Password not provided via CLI or config file (or is empty in config). Exiting.")
        sys.exit(1)

    output_directory = args.output_dir or settings['download']['output_directory']
    video_quality = args.video_quality or settings['download']['video_quality']

    if args.subtitle_lang:
        subtitle_langs = [lang.strip() for lang in args.subtitle_lang.split(',')]
    else:
        subtitle_langs = settings['download']['subtitle_languages']

    subtitle_format = settings['download']['subtitle_format']
    cookie_file_path = args.cookie_file or settings.get('cookies', {}).get('cookie_file', "cookies.txt")
    login_page_url = args.login_url or settings['login'].get('login_page_url')

    # Retry settings: CLI overrides config, which overrides defaults
    max_retries = args.max_retries if args.max_retries is not None else settings['retries']['max_attempts']
    retry_delay_seconds = args.retry_delay if args.retry_delay is not None else settings['retries']['delay_seconds']

    if login_page_url and not is_valid_url(login_page_url):
        LOGGER.warning(f"The provided login page URL '{login_page_url}' seems invalid. Proceeding with caution.")

    LOGGER.info("Initializing WebDriver...")
    chrome_options = ChromeOptions()
    if args.headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        LOGGER.info("WebDriver initialized.")

        urls_to_process = []
        if args.url:
            if not is_valid_url(args.url):
                LOGGER.error(f"The provided video page URL '{args.url}' is invalid. Exiting.")
                sys.exit(1)
            urls_to_process.append(args.url)
        elif args.url_file:
            LOGGER.info(f"Reading URLs from file: {args.url_file}")
            try:
                with open(args.url_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        url_in_file = line.strip()
                        if not url_in_file: continue
                        if is_valid_url(url_in_file):
                            urls_to_process.append(url_in_file)
                        else:
                            LOGGER.warning(f"Invalid URL found in {args.url_file} at line {line_num}: '{url_in_file}'. Skipping.")
                if not urls_to_process:
                    LOGGER.warning(f"URL file {args.url_file} was empty or contained no valid URLs.")
                else:
                    LOGGER.info(f"Loaded {len(urls_to_process)} valid URLs from {args.url_file}.")
            except FileNotFoundError:
                LOGGER.error(f"URL file {args.url_file} not found. Exiting.")
                sys.exit(1)
            except Exception as e:
                LOGGER.error(f"Error reading URL file {args.url_file}: {e}. Exiting.")
                sys.exit(1)

        if not urls_to_process:
            LOGGER.info("No valid URLs to process were found. Exiting.")
            if driver: driver.quit()
            return

        effective_login_url = login_page_url or urls_to_process[0]
        LOGGER.info(f"Attempting login using URL: {effective_login_url} (or associated login page)")
        login_successful = login_to_website(driver, effective_login_url, login_id, login_pw)

        if login_successful:
            LOGGER.info("Login assumed successful.")
            extract_and_save_cookies(driver, cookie_file_path=cookie_file_path)
            LOGGER.info(f"Cookies extracted and saved to {cookie_file_path}")
        else:
            LOGGER.error("Login failed or was not confirmed. Exiting.")
            sys.exit(1)

        for page_url in urls_to_process:
            LOGGER.info(f"Starting processing for URL: {page_url}")
            attempts = 0
            success = False
            while attempts < max_retries and not success:
                try:
                    LOGGER.info(f"Attempt {attempts + 1}/{max_retries} for {page_url}: Navigating with WebDriver...")
                    driver.get(page_url)

                    LOGGER.info(f"Attempt {attempts + 1}: Extracting media URLs from page source for {page_url}...")
                    video_sel = settings['selectors']['video_source']
                    subtitle_sel = settings['selectors']['subtitle_track']
                    media_urls = extract_media_urls(driver, page_url, video_selector=video_sel, subtitle_selector=subtitle_sel)

                    video_dl_url = media_urls.get('video_url')
                    subtitle_dl_url = media_urls.get('subtitle_url')

                    if not video_dl_url:
                        raise ValueError("No video URL extracted")
                    if not is_valid_url(video_dl_url):
                        raise ValueError(f"Invalid extracted video URL: {video_dl_url}")

                    LOGGER.info(f"Attempt {attempts + 1}: Extracted video URL: {video_dl_url}")
                    if not is_m3u8_url(video_dl_url):
                        LOGGER.warning(f"Attempt {attempts + 1}: Video URL {video_dl_url} does not appear to be an M3U8 playlist.")

                    if subtitle_dl_url:
                        if not is_valid_url(subtitle_dl_url):
                             LOGGER.warning(f"Attempt {attempts + 1}: Extracted subtitle URL '{subtitle_dl_url}' seems invalid. Ignoring.")
                             subtitle_dl_url = None
                        else:
                            LOGGER.info(f"Attempt {attempts + 1}: Extracted subtitle URL: {subtitle_dl_url}")
                    else:
                        LOGGER.info(f"Attempt {attempts + 1}: No separate subtitle URL extracted for {page_url}.")

                    LOGGER.info(f"Attempt {attempts + 1}: Calling downloader for video: {video_dl_url}")
                    download_video_with_subtitles(
                        video_url=video_dl_url, subtitle_url=subtitle_dl_url,
                        output_path=output_directory, cookie_file=cookie_file_path,
                        preferred_quality=video_quality, subtitle_langs=subtitle_langs,
                        subtitle_format=subtitle_format
                    )
                    success = True
                    LOGGER.info(f"Successfully processed URL: {page_url} after {attempts + 1} attempt(s).")
                except Exception as e:
                    attempts += 1
                    LOGGER.error(f"Attempt {attempts}/{max_retries} failed for URL {page_url}: {e}", exc_info=False)
                    if attempts < max_retries:
                        LOGGER.info(f"Retrying in {retry_delay_seconds} seconds...")
                        time.sleep(retry_delay_seconds)
                    else:
                        LOGGER.error(f"All {max_retries} attempts failed for URL {page_url}. Moving to next URL.")

            if not success:
                LOGGER.warning(f"Finished processing URL {page_url} unsuccessfully after {max_retries} attempts.")

    except Exception as e:
        LOGGER.critical(f"A critical error occurred in the main process: {e}", exc_info=True)
    finally:
        if driver:
            LOGGER.info("Quitting WebDriver...")
            driver.quit()
        LOGGER.info("Application finished.")

if __name__ == '__main__':
    main()
