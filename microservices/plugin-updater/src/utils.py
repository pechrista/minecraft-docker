import time
import hashlib
import os
import argparse
import shutil

def generate_md5(full_path, buffer_size: int = 65536):
        # Create the MD5 hash object
        hasher = hashlib.md5()

        try:
            if full_path is None:
                print(f"Error: File path is None")
                return None
            if not os.path.exists(full_path):
                print(f"Error: File not found at path: {full_path}")
                return None

            with open(full_path, 'rb') as f:
                while True:
                    # The f.read() operation uses the buffer_size variable
                    chunk = f.read(buffer_size) 
                    if not chunk:
                        break
                    hasher.update(chunk)

        except Exception as e:
            print(f"Error processing md5, given file path: {full_path}")
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
    try:
        # Check if the destination directory exists and create it if not
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        # Move the file
        shutil.move(src_path, dst_path)

    except FileNotFoundError:
        print(f"Error: Source file '{src_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")