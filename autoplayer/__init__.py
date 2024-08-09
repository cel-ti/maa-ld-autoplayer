import os
import sys
import datetime
from functools import cache
import utils.scoop as scoop_utils
from zrcl.ext_json import touch_json, read_json, write_json

# Configuration
CONFIG_DIR = os.path.expanduser("~/.config/maautohelper")
JSON_CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
UPDATE_INTERVAL = 86400  # 24 hours

# Ensure configuration directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)
touch_json(JSON_CONFIG_PATH)
json_config: dict = read_json(JSON_CONFIG_PATH)

# Function to check if last_checked key exists in the configuration
@cache
def last_check_exist():
    return "last_checked" in json_config

@cache
def last_check_fails():
    if not last_check_exist():
        return False
    
    last_checked = json_config.get("last_checked", 0)
    if (datetime.datetime.now().timestamp() - last_checked) > UPDATE_INTERVAL:
        return True
    else:
        return False
    

def update_scoop():
    if not scoop_utils.is_scoop_installed():
        print("Scoop is not installed. Please install it first.")
        exit(1)

    if not last_check_exist():
        os.system("scoop bucket add maa https://github.com/cel-ti/maa-bucket")

    if last_check_fails():
        os.system("scoop update")
        json_config["last_checked"] = datetime.datetime.now().timestamp()
        write_json(JSON_CONFIG_PATH, json_config)

    print("Scoop update check complete.")

def update_repo(branch_name="main", directories=None):
    # Fetch the latest changes from the remote
    if not last_check_fails():
        print("No repo update needed.")
        return

    os.system(f"git fetch origin {branch_name}")

    if directories:
        for directory in directories:
            os.system(f"git checkout origin/{branch_name} -- {directory}")
    else:
        # Reset the local branch to match the remote branch, keeping local changes
        os.system(f"git reset --keep origin/{branch_name}")
        # Checkout the latest changes from the remote, using theirs in case of conflicts
        os.system(f"git checkout -B {branch_name} origin/{branch_name}")

    print("Repository update complete.")

def install_requirements():
    if not last_check_fails():
        print("No pip update needed.")
        return

    print("Installing required packages...")
    os.system("pip install -U -r requirements.txt")
    print("Package installation complete.")


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

update_scoop()
install_requirements()
update_repo(directories=["configs", "cel_configs"])

print("Initialization complete.")

