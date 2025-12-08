from utils import generate_md5
import os
import requests
import shutil
import tempfile

class Plugin:
    """
    Parent class for all plugins. It also acts as a factory
    to return the correct subclass instance.
    """
    # A class attribute to store all registered subclasses (the registry)
    _plugin_registry = {}

    def __init_subclass__(cls, **kwargs):
        """
        This special method is called automatically whenever a class
        inherits from Plugin. It registers the subclass.
        """
        super().__init_subclass__(**kwargs)
        # The name used for registration is the class's own name
        cls._plugin_registry[cls.__name__] = cls
        print(f"Registered plugin: {cls.__name__}")

    def __new__(cls, plugin_dict, *args, **kwargs):
        """
        __new__ is called *before* __init__. It is responsible for
        creating and returning the new instance. We use it here to
        return an instance of the *correct subclass*.
        """
        # Get the class name from the plugin dict
        class_name = plugin_dict.get('class_name', 'Plugin')
        
        # 1. Check if the requested name is in the registry (case-insensitive)
        if class_name in cls._plugin_registry:
            subclass = cls._plugin_registry[class_name]
            instance = object.__new__(subclass)
            return instance
        else:
            # Try case-insensitive match
            for key, subclass in cls._plugin_registry.items():
                if key.lower() == class_name.lower():
                    instance = object.__new__(subclass)
                    return instance
            
            # If the name is not found, create a base Plugin instance
            print(f"No specific plugin found for {class_name}, using base Plugin class")
            instance = object.__new__(cls)
            return instance

    def __init__(self, plugin: dict):
        self.name = plugin.get("name", "")
        self.class_name = plugin.get("class_name", "Plugin")
        self.url = plugin.get("url", "")
        self.src = plugin.get("source", "")
        self.dst = plugin.get("destination", "")
        self.full_path = self.generate_full_path()
        if self.full_path:
            self.md5 = generate_md5(self.full_path)
        else:
            self.md5 = None

    def generate_full_path(self):
        if not self.name:
            return None
            
        if str(self.src) == "" or str(self.src) == ".":
            full_path = self.name
        elif str(self.src).endswith("/"):
            full_path = self.src + self.name
        else:
            full_path = self.src + "/" + self.name
        
        return full_path

    def download_latest_file(self):
        print(f"Downloading latest version of {self.name} to compare md5...")


class Paper(Plugin):
    def __init__(self, plugin: dict):
        super().__init__(plugin)

    def download_latest_file(self):
        super().download_latest_file()

        PAPER_API_BASE = "https://api.papermc.io/v2/projects/paper"
        
        # Create a temporary file with a random name
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jar')
        tmp_download_path = temp_file.name
        temp_file.close()

        try:
            # --- PHASE 1: FIND THE LATEST STABLE VERSION AND BUILD ---
            #print("Fetching latest stable PaperMC version...")
            
            # Get all available Minecraft versions for Paper
            versions_res = requests.get(PAPER_API_BASE, timeout=10)
            versions_res.raise_for_status()
            versions_data = versions_res.json()
            
            # Filter out release candidates (versions with -rc) and get the latest stable version
            versions = [v for v in versions_data['versions'] if '-rc' not in v.lower()]
            if not versions:
                # If no stable versions found, fallback to latest version
                latest_mc_version = versions_data['versions'][-1]
            else:
                latest_mc_version = versions[-1]
            #print(f"Latest Minecraft version supported by Paper: {latest_mc_version}")

            # Get the builds for that specific version
            builds_url = f"{PAPER_API_BASE}/versions/{latest_mc_version}/builds"
            builds_res = requests.get(builds_url, timeout=10)
            builds_res.raise_for_status()
            builds_data = builds_res.json()

            # Find the latest stable build number (we assume the highest number is the latest stable)
            # We filter out experimental/beta builds by looking for a status field if the API provided it,
            # but typically, the highest build number without a specific 'experimental' tag is stable.
            # Since the PaperMC API is robust, we just take the latest build number listed.
            latest_build = builds_data['builds'][-1]
            build_number = latest_build['build']
            jar_filename = latest_build['downloads']['application']['name']
            
            #print(f"Latest stable build found: {build_number}. Filename: {jar_filename}")

            # --- PHASE 2: CONSTRUCT DOWNLOAD URL AND DOWNLOAD ---
            
            download_url = f"{PAPER_API_BASE}/versions/{latest_mc_version}/builds/{build_number}/downloads/{jar_filename}"
            
            #print(f"Downloading PaperMC JAR from: {download_url}")
            
            # Use stream=True to handle large files efficiently
            with requests.get(download_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(tmp_download_path, 'wb') as f:
                    # Iterate over the response content in chunks
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            #print(f"Download complete. File saved to {tmp_download_path}")

            # Return the temporary file path for the caller to move/use as needed
            return tmp_download_path

        except requests.exceptions.RequestException as e:
            print(f"Network or request error: {e}")
            # Clean up temp file on error
            try:
                os.remove(tmp_download_path)
            except OSError:
                pass
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Clean up temp file on error
            try:
                os.remove(tmp_download_path)
            except OSError:
                pass
            return None