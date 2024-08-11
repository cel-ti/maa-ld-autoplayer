import datetime
import time
import subprocess
import pygetwindow as gw
import threading
import tempfile
from utils.config import profile_maa_config_path
from .scoop import get_install_manifest, tempdir_maa_pi_config
from .reldplayer import ldplayer

def get_window_titles():
    return [window.title for window in gw.getAllWindows() if window.title]

def close_new_windows(new_windows):
    for window in gw.getAllWindows():
        if window.title in new_windows:
            try:
                window.close()
            except Exception as e:
                print(f"Failed to close window {window.title}: {e}")

def any_window_opens(new_windows):
    for window in gw.getAllWindows():
        if window.title in new_windows:
            return True
    return False

def run_subprocess(profiledict: dict):
    subprocess_cmd = profiledict.get("subprocess_cmd")
    process = subprocess.Popen(subprocess_cmd, shell=True)
    return process

def stop_task_thread(profiledict : dict, windows : list):
    maxrun =  profiledict.get("maxrun")
    maxtime=  datetime.datetime.now() + datetime.timedelta(seconds=maxrun)
    print(f"will stop at {maxtime.isoformat()}")
    counter = 0

    while datetime.datetime.now() < maxtime and any_window_opens(windows):
        
        time.sleep(1)
        counter +=1
        if counter % 10 == 0:
            print(f"heartbeat for {profiledict["target"]}...")


    print(f"Stopping {profiledict['target']}...")
    close_new_windows(windows)
    

    ld = profiledict.get("ld", None)
    if ld:
        ldplayer().quitall()

def _create_task(profiledict: dict, blocking = True):
    ld = profiledict.get("ld", None)
    pkg = profiledict.get("pkg", None)
    waittime = profiledict.get("waittime", 60)

    initial_windows = get_window_titles()

    if ld:
        print(f"Launching {ld}")
        if pkg:
            ldplayer().launchex(name=ld, packagename=pkg)
        else:
            ldplayer().launch(name=ld)
        print(f"waiting for ldplayer to load for {waittime} seconds")
        time.sleep(waittime)

    run_subprocess(profiledict)
    time.sleep(2)

    new_windows = [window for window in get_window_titles() if window not in initial_windows]

    stop_thread = threading.Thread(target=stop_task_thread, args=(profiledict, new_windows))
    stop_thread.start()

    if blocking:
        stop_thread.join()

def run_profile(profiledict: dict, overwrite_maxrun: int = None, tempdir : tempfile.TemporaryDirectory = None):
    target = profiledict.get("target")
    
    manifest = get_install_manifest(target)
    if not manifest:
        print("Target not installed, skipped")
        return

    profiledict = profiledict.copy()
    if overwrite_maxrun:
        profiledict["maxrun"] = overwrite_maxrun

    if target == "maa-arknights" or target == "arknights":
        profiledict["subprocess_cmd"] = ["maa-arknights"]
    else:
        profiledict["subprocess_cmd"] = f"{target} -d"

    if not tempdir or not profile_maa_config_path(target):
        return _create_task(profiledict)

    with tempdir_maa_pi_config(target, profile_maa_config_path(target), tempdir):
        _create_task(profiledict)
