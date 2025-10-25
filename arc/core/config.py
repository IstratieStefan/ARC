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

def expand_paths(obj, base_dir=None):
    """
    Recursively expand ~ and $VARS in all string values
    Also normalize paths to use OS-specific separators
    """
    if isinstance(obj, dict):
        return {k: expand_paths(v, base_dir) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_paths(i, base_dir) for i in obj]
    elif isinstance(obj, str):
        # Expand both ~ and $VARS
        expanded = os.path.expandvars(os.path.expanduser(obj))
        
        # If already absolute, just normalize and return
        if os.path.isabs(expanded):
            return os.path.normpath(expanded)
        
        # If it's a relative path and we have a base_dir, resolve it
        if base_dir and ('/' in expanded or '\\' in expanded or expanded.startswith('arc')):
            # Don't modify special values (like "true", "false", single words without paths)
            if '/' in expanded or '\\' in expanded:
                expanded = os.path.join(base_dir, expanded)
                expanded = os.path.normpath(expanded)
        
        return expanded
    else:
        return obj

def load_config(config_path=None):
    """
    Load YAML config and return as ConfigDict, recursively expanding paths.
    All relative paths in the config are resolved relative to the project root.
    """
    # Try user config, else fall back to local arc.yaml
    if config_path is None:
        config_path = os.path.expanduser("~/.config/arc.yaml")
        if not os.path.exists(config_path):
            # Go up two levels from arc/core/ to find config/arc.yaml or arc.yaml
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, "config", "arc.yaml")
            if not os.path.exists(config_path):
                config_path = os.path.join(base_dir, "arc.yaml")
    
    # Get the project root directory (parent of config file)
    config_path = os.path.abspath(config_path)
    
    # More robust base_dir calculation
    if os.path.exists(config_path):
        # If config is in config/ subdirectory, go up one level
        config_dir = os.path.dirname(config_path)
        if os.path.basename(config_dir) == "config":
            base_dir = os.path.dirname(config_dir)
        else:
            # Config is in project root
            base_dir = config_dir
    else:
        # Fallback: use current working directory
        base_dir = os.getcwd()
    
    # Ensure base_dir is absolute
    base_dir = os.path.abspath(base_dir)
    
    # Debug output (can be removed later)
    import sys
    if '--debug' in sys.argv or os.environ.get('ARC_DEBUG'):
        print(f"[Config Debug] Config file: {config_path}")
        print(f"[Config Debug] Base directory: {base_dir}")
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    
    # Store the base directory and config path for debugging
    data['_base_dir'] = base_dir
    data['_config_path'] = config_path
    
    data = expand_paths(data, base_dir)
    return ConfigDict(data)

config = load_config()

# Usage:
# from config import config
# print(config.colors.background)
# print(config.screen.width)
# print(config.music_dir)
# print(config.builtin_apps[0].name)
