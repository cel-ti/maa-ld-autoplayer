import os
import subprocess
from functools import cache
import json

@cache
def is_scoop_installed():
    try:
        # Attempt to run 'scoop' with the 'which' command to check its path
        result = subprocess.run(['scoop', 'which', 'scoop'], capture_output=True, text=True, check=True, shell=True)
        
        # Check if the result contains the path to the scoop executable
        if 'scoop' in result.stdout:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        # If there's an error (scoop not found), return False
        return False
    
@cache
def get_installed():
    raw = subprocess.run(['scoop', 'list'], capture_output=True, text=True, check=True, shell=True).stdout.splitlines()
    return [x.split(' ', 1)[0] for x in raw[2:] if "maa" in x]

@cache
def get_install_manifest(name : str) -> dict:
    raw = subprocess.run(['scoop', "cat", name], capture_output=True, text=True, check=True, shell=True)
    return json.loads(raw.stdout)

@cache
def get_install_path() -> str:
    result = subprocess.run(['scoop', 'which', "scoop"], capture_output=True, text=True, check=True, shell=True)
    raw = result.stdout
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(raw))))

@cache
def get_app_path(name : str):
    manifest = get_install_manifest(name)
    assert manifest
    
    path = os.path.join(get_install_path(), name, "current")

    assert os.path.exists(path)

    return path

