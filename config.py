import os
import yaml

class ConfigDict(dict):
    """
    Allows dot notation access for nested dicts, e.g. config.colors.background
    """
    def __getattr__(self, name):
        value = self.get(name)
        if isinstance(value, dict):
            return ConfigDict(value)
        elif isinstance(value, list):
            # Optionally convert list of dicts to list of ConfigDicts
            return [ConfigDict(item) if isinstance(item, dict) else item for item in value]
        return value
    def __setattr__(self, name, value):
        self[name] = value

def expand_paths(obj):
    """
    Recursively expand ~ and $VARS in all string values
    """
    if isinstance(obj, dict):
        return {k: expand_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_paths(i) for i in obj]
    elif isinstance(obj, str):
        # Expand both ~ and $VARS
        return os.path.expandvars(os.path.expanduser(obj))
    else:
        return obj

def load_config(config_path=None):
    """
    Load YAML config and return as ConfigDict, recursively expanding paths.
    """
    # Try user config, else fall back to local arc.yaml
    if config_path is None:
        config_path = os.path.expanduser("~/.config/arc.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "arc.yaml")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    data = expand_paths(data)
    return ConfigDict(data)

config = load_config()

# Usage:
# from config import config
# print(config.colors.background)
# print(config.screen.width)
# print(config.music_dir)
# print(config.builtin_apps[0].name)
