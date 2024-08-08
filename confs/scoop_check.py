import os
import utils.scoop as scoop_utils
from zrcl.ext_json import touch_json, read_json, write_json
import datetime

# setup
os.makedirs(os.path.expanduser("~/.config/maautohelper"), exist_ok=True)
json_config_path = os.path.expanduser("~/.config/maautohelper/config.json")
touch_json(json_config_path)
json_config : dict = read_json(json_config_path)

# scoop check
if not scoop_utils.is_scoop_installed():
    print("Scoop is not installed. Please install it first.")
    exit(1)

if "last_checked" not in json_config:
    os.system("scoop bucket add maa https://github.com/cel-ti/maa-bucket")

last_checked = json_config.get("last_checked", 0)
if (datetime.datetime.now().timestamp() - last_checked) > 86400:
    os.system("scoop update")


json_config["last_checked"] = datetime.datetime.now().timestamp()
write_json(json_config_path, json_config)

print("init maa-autohelper successful")