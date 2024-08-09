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
def get_install_manifest(name : str) :
    raw = subprocess.run(['scoop', "cat", name], capture_output=True, text=True, check=True, shell=True)
    try:
        res=  json.loads(raw.stdout)
        assert isinstance(res, dict)
        return res
    except json.JSONDecodeError:
        return None

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

@cache
def get_app_config(name : str):
    return os.path.join(get_app_path(name), "config")

@cache
def supported_app_config(name : str):
    manifest = get_install_manifest(name)
    if not manifest:
        return False
    return any("MaaPiCli.exe" in x for x in manifest["bin"])

@cache
def get_maa_pi_config(name : str):
    if not supported_app_config(name):
        return None
    
    pi_conf_path = os.path.join(get_app_config(name), "maa_pi_config.json")
    if not os.path.exists(pi_conf_path):
        return None
    
    with open(pi_conf_path, "r") as f:
        res =  json.load(f)
        return res["task"]
    

def export_maa_pi_config(name : str, path : str):
    pi_config = get_maa_pi_config(name)
    if not pi_config:
        return False
    
    with open(os.path.join(path, name), "w", encoding="utf-8") as f:
        json.dump(pi_config, f, indent=2, ensure_ascii=False)

    return True




        
    

