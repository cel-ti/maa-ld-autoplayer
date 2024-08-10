import datetime
import os
from time import sleep
import click
import sys
import subprocess
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import profile_config
from utils.runner import _create_task, run_profile
from utils.scoop import export_maa_pi_config, get_app_config, get_installed, supported_app_config


@click.group()
def cli():
    pass

@cli.command()
@click.argument("app")
@click.option("--open", "-o", is_flag =True)
def config(app, open):
    if open:
        return os.startfile(get_app_config(app))

    if not supported_app_config(app):
        click.echo("Unsupported App")
        return
    os.system(app)

@cli.command()
@click.argument("app")
@click.option("--drun", "-d", default=False, is_flag=True, help="run directly")
@click.option("--timeout", "-t", default=None, help="timeout")
@click.option("--waittime", "-w", default=None, help="waittime")
@click.option("--use-profile", "-u", is_flag=True, help="use profile")
@click.option("--test", "-t", default=False, is_flag=True, help="if test, make it 100x faster")

def run(app, drun, timeout, waittime, use_profile, test):
    profile = profile_config(app)
    if not profile:
        click.echo("Unsupported App")
        return

    if timeout:
        profile["maxrun"] = int(timeout) // 100 if test else int(timeout)
    if waittime:
        profile["waittime"] = int(waittime) // 100 if test else int(waittime)

    if drun:
        try:
            result = subprocess.run([app, "-d"], shell=True, timeout=10)
            print(f"Command executed with return code {result.returncode}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
    
        return

    if use_profile:
        temp = tempfile.TemporaryDirectory()
    else:
        temp = None

    return run_profile(profile, timeout, temp)

@cli.command()
@click.option("--waittime", "-w", default=None, help="waittime")
@click.option("--test", "-t", default=False, is_flag=True, help="if test, make it 100x faster")
def auto(waittime, test):
    profile = profile_config()
    if not profile:
        click.echo("Uninited")
        return
    
    temp = tempfile.TemporaryDirectory()

    # starttime is 4 digit number for example, 1300 -> 1pm
    starttime = profile.get("starttime", None)
    if starttime:
        startts = datetime.datetime.strptime(starttime, "%H%M")
        # Get today's date
        today = datetime.date.today()

        # Combine today's date with the parsed time
        startts = datetime.datetime.combine(today, startts.time())
        now = datetime.datetime.now()
        if now.hour < startts.hour or (now.hour == startts.hour and now.minute < startts.minute):
            print(f"Not start yet, start at {starttime}")
            remainingtime = (startts - now).total_seconds()
            sleep(remainingtime)

    print("Start!")
    for p in profile.get("profile", []):
        if waittime:
            p["waittime"] = waittime
        
        omaxrun = None
        if test:
            omaxrun = p.get("maxrun")/100

        run_profile(p, omaxrun, temp)

@cli.command()
def list():
    installed = get_installed()
    for app in installed:
        print(app)

@cli.command()
@click.argument("app")
@click.option("--path", "-p", default=None)
def export(app, path):
    if not supported_app_config(app):
        click.echo("Unsupported App")
        return
    if path is None:
        path = "my_configs"
    
    export_maa_pi_config(app, path)

if __name__ == "__main__":
    import autoplayer
    cli()