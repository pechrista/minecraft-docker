import hashlib
import os
import argparse
import shutil
import logging
import subprocess
import time
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceAction(Enum):
    START = "start"
    STOP = "stop"


def wait_for_stop(base_cmd, service_name, timeout=30):
    """Polls docker ps until the service container is no longer found."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 'ps -q' returns the container ID if it exists/is running
        result = subprocess.run(
            base_cmd + ["ps", "-q", service_name],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            logger.info(f"Service {service_name} stopped successfully.")
            return True
        time.sleep(2)
    
    logger.warning(f"Timeout reached waiting for {service_name} to stop.")
    return False


def manage_service(action: ServiceAction, service_name: str, compose_path: str):
    """
    Manages a specific Docker Compose service using Enums.
    """
    # 1. Validate file exists using pathlib
    path = Path(compose_path)
    
    if not path.is_file():
        logger.error(f"Compose file not found at: {compose_path}")
        exit(1)

    # 2. Prepare the base command
    base_cmd = ["docker", "compose", "-f", str(path)]

    try:
        if action == ServiceAction.START:
            logger.info(f"Starting service: {service_name}")
            subprocess.run(base_cmd + ["up", "-d", service_name], check=True)
            
        elif action == ServiceAction.STOP:
            subprocess.run(base_cmd + ["stop", service_name], check=True)
            if wait_for_stop(base_cmd, service_name):
                subprocess.run(base_cmd + ["rm", "-f", service_name], check=True)

    except subprocess.CalledProcessError:
        # Using .exception automatically adds the stack trace
        logger.exception(f"Failed to {action.value} service: {service_name}")


def generate_md5(full_path, buffer_size: int = 65536):
        logger.debug(f"Generating md5 for: {full_path}")
        # Create the MD5 hash object
        hasher = hashlib.md5()

        try:
            if full_path is None:
                logger.error(f"Error: File path is None")
                return None
            if not os.path.exists(full_path):
                logger.error(f"Error: File not found at path: {full_path}")
                return None

            with open(full_path, 'rb') as f:
                while True:
                    # The f.read() operation uses the buffer_size variable
                    chunk = f.read(buffer_size) 
                    if not chunk:
                        break
                    hasher.update(chunk)

        except Exception as e:
            logger.error(f"Error processing md5, given file path: {full_path}")
            raise Exception(e)
        
        return hasher.hexdigest()

def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Run the application with a specified configuration file."
    )
    
    # Define the runtime argument: --config
    parser.add_argument(
        '--config',
        type=str,
        required=True, # Makes the argument mandatory
        help='Path to the application configuration file (e.g., config.ini)'
    )

    return parser.parse_args()


def move_file(src_path: str, dst_path: str):
    logger.debug(f"Moving file from {src_path} to {dst_path}")

    try:
        # Move the file
        shutil.move(src_path, dst_path)

    except FileNotFoundError:
        logger.error(f"Error: Source file '{src_path}' not found.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")