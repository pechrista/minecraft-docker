import hashlib
import os
import argparse
import shutil
import logging

logger = logging.getLogger(__name__)

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