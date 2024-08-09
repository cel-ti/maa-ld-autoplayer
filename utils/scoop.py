from contextlib import contextmanager
import os
import shutil
import subprocess
from functools import cache
import json
import tempfile

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


def import_maa_pi_config(name : str, path : str):
    if not os.path.exists(path):
        return False
    
    with open(path, "r", encoding="utf-8") as f:
        pi_config = json.load(f)

    pi_config_is_list = isinstance(pi_config, list)

    base = os.path.join(get_app_config(name), "maa_pi_config.json")
    
    if not os.path.exists(base):
        with open(base, "w", encoding="utf-8") as f:
            if not pi_config_is_list:
                json.dump(pi_config, f, indent=2, ensure_ascii=False)
            else:
                json.dump({"task":pi_config}, f, indent=2, ensure_ascii=False)
        return True

    if pi_config_is_list:
        with open(base, "r", encoding="utf-8") as f:
            base_config = json.load(f)

    with open(base, "w", encoding="utf-8") as f:
        if pi_config_is_list:
            base_config["task"] = pi_config
            json.dump(base_config, f, indent=2, ensure_ascii=False)
        else:
            json.dump(pi_config, f, indent=2, ensure_ascii=False)

    return True

@contextmanager
def tempdir_maa_pi_config(name : str, path : str, tempdir : tempfile.TemporaryDirectory):
    """
    temporally injecting tasks into the maa_pi_config.json file, and create a copy of the original file to tempdir
    """
    if not os.path.exists(path):
        yield
        return
    
    app_config = os.path.join(get_app_config(name), "maa_pi_config.json")
    if not os.path.exists(app_config):
        raise FileNotFoundError(f"config file {app_config} not found")
    
    shutil.copy(app_config, os.path.join(tempdir.name, name))

    import_maa_pi_config(name, path)
    try:
        yield
    finally:
        # remove existing
        import_maa_pi_config(name, os.path.join(tempdir.name, name))
    