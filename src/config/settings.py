import json
import os
import copy

DEFAULT_SETTINGS = {
    "login": {
        "username": "",
        "password": ""
    },
    "download": {
        "output_directory": "./downloads",
        "video_quality": "best",
        "subtitle_languages": ["en", "ko"],
        "subtitle_format": "srt"
    },
    "selectors": {
        "video_source": "#__next > div > div.drawer-content.overflow-scroll > main > div > div > div > div > div:nth-child(1) > video > source",
        "subtitle_track": "#hls-subtitles-0"
    },
    "retries": {
        "max_attempts": 3,
        "delay_seconds": 10
    }
}

def load_settings(config_path='config.json'):
    """
    Loads settings from a JSON configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The final settings dictionary, merged with default settings.
    """
    settings = copy.deepcopy(DEFAULT_SETTINGS)  # Start with a deep copy of default settings

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_from_file = json.load(f)

            # Merge loaded settings with default settings
            # Nested dictionaries need to be updated individually
            for key, value in config_from_file.items():
                if isinstance(value, dict) and key in settings:
                    settings[key].update(value)
                else:
                    settings[key] = value
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Error reading or parsing {config_path}: {e}. Using default settings.")
    else:
        print(f"Warning: {config_path} not found. Using default settings.")

    return settings

if __name__ == '__main__':
    # Example usage:
    # Create a dummy config.json for testing
    dummy_config = {
        "login": {"username": "testuser"},
        "download": {"output_directory": "/tmp/my_downloads"}
    }
    with open('config.json', 'w') as f:
        json.dump(dummy_config, f, indent=2)

    settings = load_settings()
    print("Loaded settings:")
    print(json.dumps(settings, indent=2))

    # Clean up dummy config.json
    if os.path.exists('config.json'):
        os.remove('config.json')

    # Test case where config.json does not exist
    print("\nTesting with no config.json:")
    settings_no_config = load_settings('non_existent_config.json')
    print("Loaded settings (no config file):")
    print(json.dumps(settings_no_config, indent=2))

    # Test case with invalid JSON
    with open('invalid_config.json', 'w') as f:
        f.write("{'invalid_json': True,}") # Invalid JSON

    print("\nTesting with invalid config.json:")
    settings_invalid_config = load_settings('invalid_config.json')
    print("Loaded settings (invalid config file):")
    print(json.dumps(settings_invalid_config, indent=2))

    if os.path.exists('invalid_config.json'):
        os.remove('invalid_config.json')

    # Test with a config that overrides only some nested values
    partial_override_config = {
        "download": {"video_quality": "1080p"},
        "selectors": {"video_source": "new_video_selector"},
        "retries": {"max_attempts": 5}
    }
    with open('partial_config.json', 'w') as f:
        json.dump(partial_override_config, f, indent=2)

    print("\nTesting with partial override config.json:")
    settings_partial_override = load_settings('partial_config.json')
    print("Loaded settings (partial override):")
    print(json.dumps(settings_partial_override, indent=2))
    # Check specific retry setting
    assert settings_partial_override['retries']['max_attempts'] == 5
    assert settings_partial_override['retries']['delay_seconds'] == DEFAULT_SETTINGS['retries']['delay_seconds'] # Should use default
    if os.path.exists('partial_config.json'):
        os.remove('partial_config.json')

    # Test loading retry settings when config file doesn't exist (should use defaults)
    print("\nTesting retry settings with no config file:")
    settings_no_config_retry = load_settings('non_existent_config_for_retry_test.json')
    print("Loaded settings (no config for retry):")
    print(json.dumps(settings_no_config_retry['retries'], indent=2))
    assert settings_no_config_retry['retries']['max_attempts'] == DEFAULT_SETTINGS['retries']['max_attempts']
    assert settings_no_config_retry['retries']['delay_seconds'] == DEFAULT_SETTINGS['retries']['delay_seconds']

    print("\nAll settings.py tests seem to pass based on output.")
