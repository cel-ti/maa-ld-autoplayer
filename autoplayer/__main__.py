import os
import click
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autoplayer.init import init
from utils.config import profile_config
from utils.runner import run_profile
from utils.scoop import export_maa_pi_config, get_installed, supported_app_config

@click.group()
def cli():
    pass

@cli.command()
@click.argument("app")
def config(app):
    if not supported_app_config(app):
        click.echo("Unsupported App")
        return
    os.system(app)

@cli.command()
@click.argument("app")
@click.option("--drun", "-d", default=False, is_flag=True, help="run directly")
@click.option("--timeout", "-t", default=None, help="timeout")
def run(app, drun, timeout):
    if not supported_app_config(app):
        click.echo("Unsupported App")
        return

    if drun:
        try:
            result = subprocess.run([app, "-d"], shell=True, timeout=10)
            print(f"Command executed with return code {result.returncode}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
    
        return

    config = profile_config()
    for profile in config.get("profile", []):
        if profile["target"] == app:
            return run_profile(profile, timeout)

    click.echo("No profile found")

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
    init()
    cli()