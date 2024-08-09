
import signal
from time import sleep
from .scoop import get_install_manifest
from .reldplayer import ldplayer
import threading 
import subprocess

def _run_thread(profiledict : dict):
    ld = profiledict.get("ld", None)
    subprocess_cmd = profiledict.get("subprocess_cmd", None)
    maxrun = profiledict.get("maxrun")
    process = subprocess.Popen(subprocess_cmd, shell=True)
    try:
        process.wait(timeout=maxrun)
    except subprocess.TimeoutExpired:
        print("Max run time reached, terminating process")
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=5)  # Allow a grace period for shutdown
        except subprocess.TimeoutExpired:
            process.kill()

    # killing ld proc
    if ld:
        ldplayer().quitall()

def _create_profile_thread(profiledict : dict):
    maxrun = profiledict.get("maxrun")
    ld = profiledict.get("ld", None)
    pkg = profiledict.get("pkg", None)

    if ld:
        if pkg:
            ldplayer().launchex(name=ld, packagename=pkg)
        else:
            ldplayer().launch(name=ld)
        sleep(60)

    # Start the target in a separate thread
    target_thread = threading.Thread(target=_run_thread, args=(profiledict,))
    target_thread.start()

    # Wait for the maxrun time, then signal the thread to stop
    sleep(maxrun)
    if target_thread.is_alive():
        print("Stopping target process after maxrun")
        target_thread.join(timeout=5)  # Join with a timeout to allow for cleanup
    
def run_profile(profiledict : dict, overwrite_maxrun : int = None):
    target = profiledict.get("target")
    manifest = get_install_manifest(target)
    if not manifest:
        print("Target not installed, skipped")
        return
    
    profiledict = profiledict.copy()
    if overwrite_maxrun:
        profiledict["maxrun"] = overwrite_maxrun

    profiledict["subprocess_cmd"] = [target, "-d"]

    _create_profile_thread(profiledict)
