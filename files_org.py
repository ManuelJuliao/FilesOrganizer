import os
import json
import shutil
from tkinter import filedialog
from datetime import datetime

# Default configuration
DEFAULT_CONFIG = {
    "folders": {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "Videos": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
        "Audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h"]
    },
    "settings": {
        "log_location": "app"  # "app" for next to executable, "target" for organized folder
    }
}

def get_default_config():
    """Return a copy of the default configuration"""
    return DEFAULT_CONFIG.copy()

def get_default_settings():
    """Return a copy of the default settings"""
    return DEFAULT_CONFIG["settings"].copy()

def load_config_from_file(file_path):
    """Load configuration from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
            # Handle old config format
            if "folders" not in config:
                config = {
                    "folders": config,
                    "settings": {
                        "log_location": "app"
                    }
                }
            return config
    except Exception as e:
        raise Exception(f"Failed to load configuration: {str(e)}")

def save_config_to_file(file_path, config):
    """Save configuration to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        raise Exception(f"Failed to save configuration: {str(e)}")

def load_settings():
    """Load settings from settings.json"""
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except:
            return get_default_settings()
    return get_default_settings()

def save_settings(settings):
    """Save settings to settings.json"""
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    try:
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        raise Exception(f"Failed to save settings: {str(e)}")

def validate_config(config):
    """Validate the configuration structure"""
    if not isinstance(config, dict):
        return False
    if "folders" not in config:
        return False
    folders = config["folders"]
    for folder, extensions in folders.items():
        if not isinstance(extensions, list):
            return False
        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith('.'):
                return False
    return True

def pick_dir(file, config):
    """Find the appropriate directory for a file based on its extension"""
    _, ext = os.path.splitext(file)
    for folder, extensions in config["folders"].items():
        if ext.lower() in [e.lower() for e in extensions]:
            return folder
    return None

def log_file_movement(log_file, source_path, destination_path, timestamp):
    """Log file movement to a log file"""
    try:
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Moved: {source_path} -> {destination_path}\n")
    except Exception as e:
        print(f"Failed to log file movement: {str(e)}")

def organize_dir(dir_path, config):
    """Organize files in the directory based on the configuration"""
    try:
        # Get log location setting
        log_location = config.get("settings", {}).get("log_location", "app")
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if log_location == "target":
            log_file = os.path.join(dir_path, f"file_organization_{timestamp}.log")
        else:  # "app" or default
            log_file = os.path.join(os.path.dirname(__file__), f"file_organization_{timestamp}.log")
        
        # Create folders if they don't exist
        for folder in config["folders"].keys():
            folder_path = os.path.join(dir_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Move files to appropriate folders
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                target_folder = pick_dir(file, config)
                if target_folder:
                    target_path = os.path.join(dir_path, target_folder, file)
                    shutil.move(file_path, target_path)
                    # Log the file movement
                    log_file_movement(log_file, file_path, target_path, timestamp)
        return True
    except Exception as e:
        print(f"Error organizing directory: {str(e)}")
        return False

def start_organizing():
    """Start the file organization process"""
    dir_path = filedialog.askdirectory()
    if dir_path:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        config = load_config_from_file(config_path) if os.path.exists(config_path) else get_default_config()
        if organize_dir(dir_path, config):
            print("Files organized successfully!")
        else:
            print("Failed to organize files")

def get_latest_log_file():
    """Get the path of the most recent log file"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(__file__)
        # Get all log files
        log_files = [f for f in os.listdir(script_dir) if f.startswith('file_organization_') and f.endswith('.log')]
        if not log_files:
            return None
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(script_dir, x)), reverse=True)
        return os.path.join(script_dir, log_files[0])
    except Exception as e:
        print(f"Error getting latest log file: {str(e)}")
        return None

def read_log_file(log_file):
    """Read the contents of a log file"""
    try:
        if not log_file or not os.path.exists(log_file):
            return "No log file found."
        with open(log_file, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading log file: {str(e)}"

if __name__ == "__main__":
    start_organizing()