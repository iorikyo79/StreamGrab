import yt_dlp
import os
import logging

# Configure basic logging
# In a larger app, this might be handled by a central logger from utils/logger.py
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(module)s - %(message)s')

def default_progress_hook(d):
    """A simple progress hook for yt-dlp."""
    if d['status'] == 'finished':
        logging.info(f"Done downloading, now converting ... (Filename: {d.get('filename', d.get('info_dict', {}).get('filepath', 'N/A'))})")
    if d['status'] == 'downloading':
        # Print progress every time, or throttle it
        filename = d.get('filename', d.get('info_dict', {}).get('filepath', 'N/A'))
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')

        if total_bytes:
            progress = downloaded_bytes / total_bytes * 100
            logging.info(f"Downloading {filename}: {progress:.2f}% ({downloaded_bytes}/{total_bytes} bytes)")
        else:
            logging.info(f"Downloading {filename}: {downloaded_bytes} bytes (total size unknown)")
    # You can add more details like speed, ETA etc. if desired

def download_video_with_subtitles(
    video_url: str,
    subtitle_url: str, # Can be None
    output_path: str,
    cookie_file: str = "cookies.txt",
    preferred_quality: str = "best",
    subtitle_langs: list = None, # Default to None, handle in options
    subtitle_format: str = "srt/vtt/best"
):
    """
    Downloads a video and its subtitles using yt-dlp.

    Args:
        video_url: URL of the video to download.
        subtitle_url: URL of the subtitle file (if separate and known). Can be None.
        output_path: Directory where the media should be saved.
        cookie_file: Path to the cookies file (e.g., cookies.txt).
        preferred_quality: Preferred video quality (e.g., 'best', '1080p').
        subtitle_langs: List of preferred subtitle languages (e.g., ['en', 'es']).
        subtitle_format: Preferred subtitle format (e.g., 'srt', 'vtt', 'best').
    """
    if subtitle_langs is None:
        subtitle_langs = ['en', 'ko'] # Default if not provided

    if not video_url:
        logging.error("No video URL provided. Cannot proceed with download.")
        return

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Base yt-dlp options
    ydl_base_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'cookiefile': cookie_file if cookie_file and os.path.exists(cookie_file) else None,
        'quiet': False,
        'noplaylist': True,
        'progress_hooks': [default_progress_hook],
        'merge_output_format': 'mp4/mkv', # Often useful if 'best' gets separate video/audio
        # 'verbose': True, # Uncomment for very detailed yt-dlp logs
    }

    # Options for video download (may also get subtitles if embedded or easily found)
    video_opts = ydl_base_opts.copy()
    video_opts.update({
        'format': preferred_quality,
        'writesubtitles': True,
        'writeautomaticsub': False, # Do not download auto-generated subs if specific languages are requested
        'subtitleslangs': subtitle_langs,
        'subtitlesformat': subtitle_format,
    })

    logging.info(f"Attempting to download video from: {video_url}")
    logging.debug(f"yt-dlp video options: {video_opts}")

    try:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([video_url])
        logging.info(f"Video download attempt finished for URL: {video_url}")
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"yt-dlp DownloadError for video URL {video_url}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during video download for {video_url}: {e}")

    # Separate subtitle download if subtitle_url is distinct and provided
    # This is useful if subtitles are on a completely different URL or need special handling.
    # Note: yt-dlp might have already downloaded subtitles if they were found with the video.
    # This section ensures a specific subtitle URL is also processed if given.
    if subtitle_url and subtitle_url != video_url:
        logging.info(f"Attempting to download separate subtitles from: {subtitle_url}")

        subtitle_specific_opts = ydl_base_opts.copy()
        subtitle_specific_opts.update({
            'writesubtitles': True,
            'subtitleslangs': subtitle_langs, # Use same lang preferences
            'subtitlesformat': subtitle_format,
            'skip_download': True, # Crucial: only download subtitles
        })

        logging.debug(f"yt-dlp subtitle-specific options: {subtitle_specific_opts}")
        try:
            with yt_dlp.YoutubeDL(subtitle_specific_opts) as sub_ydl:
                sub_ydl.download([subtitle_url]) # Download subtitles for the subtitle_url
            logging.info(f"Separate subtitle download attempt finished for URL: {subtitle_url}")
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"yt-dlp DownloadError for subtitle URL {subtitle_url}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during subtitle download for {subtitle_url}: {e}")
    elif subtitle_url:
        logging.info("Subtitle URL is the same as video URL or was not provided for separate download.")


if __name__ == '__main__':
    print("--- Media Downloader Example ---")

    # This is a conceptual example. To run it for real, you would need:
    # 1. Valid video_url and potentially subtitle_url.
    # 2. yt-dlp installed and working.
    # 3. A cookies.txt file if the site requires login.

    # Create a dummy cookies.txt for the example if it doesn't exist
    # In a real scenario, this file would be populated by the login process.
    if not os.path.exists("cookies.txt"):
        with open("cookies.txt", "w") as f:
            f.write("# Dummy cookies.txt for example\n")

    # Example placeholder URLs (these will likely fail as they are not real media)
    # Replace with actual test URLs if you have them.
    # For local M3U8 testing, you can use 'file:///path/to/your/file.m3u8'
    test_video_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" # A known public M3U8 test stream
    test_subtitle_url = None # No separate subtitle URL for this example, yt-dlp might find embedded ones
    # test_subtitle_url = "https://example.com/path/to/subtitles.srt" # If you have a separate one

    test_output_directory = "downloaded_media"

    logging.info("Starting conceptual download example...")
    logging.info(f"Video URL: {test_video_url}")
    logging.info(f"Subtitle URL: {test_subtitle_url if test_subtitle_url else 'Not provided (will rely on video stream)'}")
    logging.info(f"Output directory: {test_output_directory}")
    logging.info(f"Cookie file: cookies.txt (dummy created if not present)")

    # Call the download function
    # Note: This will actually attempt to download if yt-dlp is installed and URLs are valid.
    # For a purely conceptual run printing options, you'd have to modify the function
    # or not use `with yt_dlp.YoutubeDL(video_opts) as ydl:` context manager.

    # To make this example runnable without actual download attempts in a CI/testing environment
    # where network calls might be restricted or undesirable, one might typically mock yt_dlp.YoutubeDL.
    # For this subtask, we'll assume it's okay to define the call.

    print("\nConceptual call to download_video_with_subtitles:")
    print(f"  Video URL: {test_video_url}")
    print(f"  Subtitle URL: {test_subtitle_url}")
    print(f"  Output Path: {test_output_directory}")
    print("  (This would actually run yt-dlp if URLs are valid and yt-dlp is installed)\n")

    # Example of how options would be formed (simplified, not the full internal dict)
    print("Example yt-dlp video options that would be used (simplified):")
    print(f"  outtmpl: {os.path.join(test_output_directory, '%(title)s.%(ext)s')}")
    print(f"  format: best")
    print(f"  writesubtitles: True")
    print(f"  subtitleslangs: ['en', 'ko']")
    print(f"  cookiefile: cookies.txt")

    # To actually run it for this example (requires yt-dlp and internet):
    # download_video_with_subtitles(
    #     video_url=test_video_url,
    #     subtitle_url=test_subtitle_url,
    #     output_path=test_output_directory,
    #     cookie_file="cookies.txt",
    #     preferred_quality="best",
    #     subtitle_langs=['en', 'ja'], # Example: English and Japanese
    #     subtitle_format="srt/vtt"
    # )

    if os.path.exists("cookies.txt") and open("cookies.txt").read().strip() == "# Dummy cookies.txt for example":
        # os.remove("cookies.txt") # Clean up dummy file
        print("Dummy cookies.txt was present for the example.")

    print("\nConceptual download example finished.")
    print("To perform a real download, uncomment the call to download_video_with_subtitles and provide valid URLs.")
