
from functools import cache
import json
import os
import toml

@cache
def profile_config(name : str = None):
    cel_path = os.path.join("cel_configs", "config.toml")
    my_path = os.path.join("my_configs", "config.toml")

    if os.path.exists(my_path):
        target = my_path
    elif os.path.exists(cel_path):
        target = cel_path
    else:
        return 

    with open(target, "r") as f:
        data = toml.load(f)

    if name:
        for profile in data.get("profile", []):
            if target == name or target == f"maa-{name}":
                return profile

        return None

    return data


@cache
def profile_maa_config(name : str):
    name = f"maa-{name}" if "maa" not in name else name
    cel_path = os.path.join("cel_configs", name)
    my_path = os.path.join("my_configs", name)

    if os.path.exists(my_path):
        target = my_path
    elif os.path.exists(cel_path):
        target = cel_path
    else:
        return None
    
    with open(target, "r") as f:
        data = json.load(f)
        return data
    
    



