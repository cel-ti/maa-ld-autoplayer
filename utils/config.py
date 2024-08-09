
from functools import cache
import json
import os
import toml

@cache
def profile_config(name : str = None):
    cel_path = os.path.join("cel_configs", name if name else "config.toml")
    my_path = os.path.join("my_configs", name if name else "config.toml")

    if os.path.exists(my_path):
        target = my_path
    elif os.path.exists(cel_path):
        target = cel_path
    else:
        return 

    if name:
        with open(target, "r") as f:
            return json.loads(f.read())
    else:
        with open(target, "r") as f:
            return toml.load(f)
        





