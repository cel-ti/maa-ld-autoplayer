import os

print("updating repo...")

def updatng_all(branch_name = "main"):
    # Fetch the latest changes from the remote
    os.system(f"git fetch origin {branch_name}")

    # Reset the local branch to match the remote branch, keeping local changes
    os.system(f"git reset --keep origin/{branch_name}")

    # Checkout the latest changes from the remote, using theirs in case of conflicts
    os.system(f"git checkout -B {branch_name} origin/{branch_name}")

def updating_some_directories(branch_name = "main", *directories):

    # Fetch the latest changes from the remote
    os.system(f"git fetch origin {branch_name}")

    for directory in directories:
        os.system(f"git checkout origin/{branch_name} -- {directory}")