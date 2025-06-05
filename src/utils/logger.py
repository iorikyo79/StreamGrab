import logging
import sys

DEFAULT_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logger(name='streamgrab_logger', level=logging.INFO, log_file=None, formatter=DEFAULT_FORMATTER):
    """
    Configures and returns a logger instance.

    Args:
        name (str): The name of the logger.
        level (int): The minimum logging level (e.g., logging.INFO, logging.DEBUG).
        log_file (str, optional): Path to a file where logs should be saved.
                                  If None, only console logging is enabled.
        formatter (logging.Formatter, optional): The log message formatter.
                                                 Defaults to DEFAULT_FORMATTER.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if logger was already configured elsewhere or in tests
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout) # Use sys.stdout for consistency
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a') # Append mode
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Use a basic print here as logger might not be fully set up if file handler fails
            print(f"Warning: Could not set up file logger at {log_file}: {e}", file=sys.stderr)


    # Set propagation to False if you don't want messages to go up to the root logger,
    # especially if the root logger has its own handlers.
    # For this setup, we might want to keep it True if other parts of the app
    # might rely on root logger configuration, or False if this logger is meant to be standalone.
    # logger.propagate = False

    return logger

# Global Logger instance (optional, but a common pattern)
# This creates a default logger when the module is imported.
# Other modules can then 'from src.utils.logger import LOGGER'
# For more flexibility (e.g., in testing or if multiple distinct loggers are needed),
# modules might call setup_logger() themselves.
LOGGER = setup_logger()

if __name__ == '__main__':
    # --- Test default LOGGER ---
    LOGGER.debug("This is a debug message from the default LOGGER (should not appear if level is INFO).")
    LOGGER.info("This is an info message from the default LOGGER.")
    LOGGER.warning("This is a warning message from the default LOGGER.")
    LOGGER.error("This is an error message from the default LOGGER.")
    LOGGER.critical("This is a critical message from the default LOGGER.")

    # --- Test custom logger with file output ---
    test_log_file = "test_app.log"
    file_logger = setup_logger(name="my_file_logger", level=logging.DEBUG, log_file=test_log_file)

    file_logger.debug(f"This debug message should go to console and {test_log_file}.")
    file_logger.info(f"This info message should also go to console and {test_log_file}.")

    print(f"\nCheck '{test_log_file}' for logged messages from 'my_file_logger'.")

    # --- Test logger with a different name and no file ---
    another_logger = setup_logger(name="another_console_logger", level=logging.INFO)
    another_logger.info("Info message from another_console_logger.")

    # Demonstrate that loggers are distinct or part of a hierarchy
    # root_logger_test = logging.getLogger("root_test")
    # root_logger_test.error("Error from a logger not explicitly set up by setup_logger (goes to root if root is configured).")

    # Cleanup test log file (optional)
    # import os
    # if os.path.exists(test_log_file):
    #     os.remove(test_log_file)
    #     print(f"Cleaned up {test_log_file}.")
