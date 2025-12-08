import configparser
import sys
import os
import time
from plugins import Plugin
from utils import setup_argparse
from utils import generate_md5
from utils import move_file

###
### Class Definitions
###

class Settings:
    """Object to hold environment settings from config
    """
    def __init__(self, settings: dict):
        self.frequency_hours = settings["frequency_hours"]

###
### Functions
###


def parse_config_file(file_path: str) -> tuple[Settings, list[Plugin]]:
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
            print(f"Error: Configuration file not found or could not be read at '{file_path}'.", file=sys.stderr)
            return {}

        # populate settings object from config
        try:
            settings = Settings(dict(config.items("settings")))
        except KeyError as e:
            print(f"Error: Missing required field in settings: {e}", file=sys.stderr)
            exit(1)

        # populate plugins list from config
        for section in config.sections():
            # read all config sections that start with "plugin:"
            section = section.lower()
            if section.startswith("plugin:"):
                plugin = Plugin(dict(config.items(section)))
                plugins.append(plugin)

    except configparser.Error as e:
        print(f"Error parsing configuration file '{file_path}': {e}", file=sys.stderr)
        return {}

    return settings,plugins


def update_plugin(plugin: Plugin):

    # pull latest plugin from url into tmp
    download_file_path = plugin.download_latest_file()
    
    # check if download was successful
    if download_file_path is None:
        print(f"Failed to download {plugin.name}, skipping...")
        return

    try:
        # generate hash
        md5 = generate_md5(download_file_path)
        
        # check if md5 generation was successful
        if md5 is None:
            print(f"Failed to generate MD5 for {plugin.name}, skipping...")
            return
        
        # compare against existing plugin hash 
        if md5 != plugin.md5:
            print(f"Newer version of {plugin.name} detected. Moving to {plugin.dst}/{plugin.name}")
            move_file(download_file_path, f"{plugin.dst}/{plugin.name}")
        else:
            print(f"No update required for {plugin.name}")
    
    finally:
        # Clean up the temporary file
        if download_file_path and os.path.exists(download_file_path):
            try:
                os.remove(download_file_path)
                #print(f"Cleaned up temporary file: {download_file_path}")
            except OSError as e:
                print(f"Warning: Failed to clean up temporary file {download_file_path}: {e}")


def shutdown_mc_server():
    print("todo... shutdown mc server")    


def start_mc_server():
    print("todo...start mc server")


###
### Main
###

def main():
    # setup args and get config file path
    args = setup_argparse()
    
    # initial parse of config file (Paper class is already registered)
    settings,plugins = parse_config_file(args.config)

    # recurring parse of config file
    while True:
        print(f"Sleeping for {settings.frequency_hours} hours...")
        
        # wait for the specified frequency
        time.sleep(int(settings.frequency_hours) * 3600)

        # shut down minecraft server
        shutdown_mc_server()

        # re-parse the config file
        settings,plugins = parse_config_file(args.config)

        # attempt to update the plugins
        for plugin in plugins:
            update_plugin(plugin)

        # start back up minecraft server
        start_mc_server()

if __name__ == "__main__":
    main()