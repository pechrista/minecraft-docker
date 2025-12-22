import configparser
import sys
import os
import time
import yaml
import signal
import logging
from plugins import Plugin
from utils import setup_argparse
from utils import generate_md5
from utils import move_file
from utils import ServiceAction
from utils import manage_service

DEFAULT_FREQUENCY_HOURS = "24"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_DOCKER_COMPOSE_SERVICE_NAME = "minecraft"
DEFAULT_DOCKER_COMPOSE_PATH = "."

# setup logger
logger = logging.getLogger(__name__)

###
### Class Definitions
###

class Settings:
    """Object to hold environment settings from config
    """
def __init__(self):
        # Read from Environment Variables instead of config dict
        self.frequency_hours = os.getenv("FREQUENCY_HOURS", DEFAULT_FREQUENCY_HOURS)
        self.log_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
        
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.debug(f"Log level set to: {self.log_level}")
        
        self.docker_compose_service_name = os.getenv("DOCKER_COMPOSE_SERVICE_NAME", DEFAULT_DOCKER_COMPOSE_SERVICE_NAME)
        self.docker_compose_path = os.getenv("DOCKER_COMPOSE_PATH", DEFAULT_DOCKER_COMPOSE_PATH)

###
### Functions
###

def signal_handler(sig, frame):
    """
    Custom handler function for SIGINT signal.
    """
    print('\nSIGINT or CTRL-C detected. Performing cleanup...')
    # Place your cleanup code here
    sys.exit(0)


def parse_config_file(file_path: str) -> tuple[list[Plugin]]:
    """
    Reads and parses a configuration file using configparser.

    Args:
        file_path: The path to the configuration file.

    Returns:
        A Settings object containing environment settings.
        A list of Plugin objects containing plugin configurations.
    """
    config = configparser.ConfigParser()
    plugins = []

    try:
        # config.read() returns a list of successfully read filenames
        files_read = config.read(file_path)
        
        if not files_read:
            # If the file wasn't found or couldn't be read
            logger.error(f"Error: Configuration file not found or could not be read at '{file_path}'.")
            return {}

        # populate plugins list from config
        for section in config.sections():
            # read all config sections that start with "plugin:"
            section = section.lower()
            if section.startswith("plugin:"):
                plugin = Plugin(dict(config.items(section)))
                logger.debug(f"Successfully registered plugin: {plugin.name}")
                plugins.append(plugin)

    except configparser.Error as e:
        logger.error(f"Error parsing configuration file '{file_path}': {e}")
        return {}

    return plugins


def update_plugin(plugin: Plugin) -> bool:
    """Update a single plugin, returns True if updated
    
    Args:
        plugin: Plugin object to update
        
    Returns:
        bool: True if plugin was updated, False otherwise
    """

    # pull latest plugin from url into tmp
    logger.debug(f"Downloading latest available jar for: {plugin.name}")
    download_file_path = plugin.download_latest_file()
    
    # check if download was successful
    if download_file_path is None:
        logger.error(f"Failed to download {plugin.name}, skipping...")
        return False

    try:
        # generate hash
        md5 = generate_md5(download_file_path)
        logger.debug(f"Generated md5 for {plugin.name}: {md5}")
        
        # check if md5 generation was successful
        if md5 is None:
            logger.error(f"Failed to generate MD5 for {plugin.name}, skipping...")
            return False
        
        # compare against existing plugin hash
        if not plugin.md5:
            logger.info(f"No jar previously downloaded for: {plugin.name}. Saving downloaded file to {plugin.full_path}...")
            move_file(download_file_path, plugin.full_path)
            return True
        elif md5 != plugin.md5:
            logger.info(f"Newer version of {plugin.name} downloaded! Saving to {plugin.full_path}")
            move_file(download_file_path, plugin.full_path)
            return True
        else:
            logger.info(f"No update required for {plugin.name}")
            return False
    
    finally:
        # Clean up the temporary file
        if download_file_path and os.path.exists(download_file_path):
            try:
                os.remove(download_file_path)
            except OSError as e:
                logger.error(f"Warning: Failed to clean up temporary file {download_file_path}: {e}")

###
### Main
###

def main():
    # setup args and get config file path
    args = setup_argparse()

    # Now parse the full config file with log level
    plugins = parse_config_file(args.config)

    # load env vars into settings
    settings = Settings()

    # recurring parse of config file
    while True:
        # wait for the specified frequency
        logger.info(f"Sleeping for {settings.frequency_hours} hours...")
        time.sleep(int(settings.frequency_hours) * 3600)

        # Re-parse config file each iteration to pick up any new plugins
        plugins = parse_config_file(args.config)
        logger.info(f"Found {len(plugins)} plugin(s) in config")

        # stop mc server for plugin check
        logger.info("Stopping minecraft server for plugin check...")
        manage_service(ServiceAction.STOP, settings.docker_compose_service_name, settings.docker_compose_path)
        
        # Update plugins
        for plugin in plugins:
            logger.info(f"Checking updates for {plugin.name}...")
            wasUpdated = update_plugin(plugin)

        # restart mc server
        logger.info("Restarting minecraft server")
        manage_service(ServiceAction.START, settings.docker_compose_service_name, settings.docker_compose_path)   

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()