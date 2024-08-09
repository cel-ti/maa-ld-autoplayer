
import signal
from time import sleep
from .scoop import get_install_manifest
from .reldplayer import ldplayer
import threading 
import subprocess

def _create_profile_thread(profiledict : dict):
    maxrun = profiledict.get("maxrun")
    target = profiledict.get("target")
    ld = profiledict.get("ld", None)
    pkg = profiledict.get("pkg", None)

    if ld:
        if pkg:
            ldplayer().launchex(name=ld, packagename=pkg)
        else:
            ldplayer().launch(name=ld)
        sleep(60)

    # Function to run the target process
    def run_target():
        process = subprocess.Popen([target, "-d"], shell=True)
        try:
            process.wait(timeout=maxrun)
        except subprocess.TimeoutExpired:
            print("Max run time reached, terminating process")
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=5)  # Allow a grace period for shutdown
            except subprocess.TimeoutExpired:
                process.kill()

    # Start the target in a separate thread
    target_thread = threading.Thread(target=run_target)
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

    _create_profile_thread(profiledict)
