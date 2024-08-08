import os


if __name__ == "__main__":
    print("updating...")
    branch_name = "main"  # Change this to your specific branch

    # Fetch the latest changes from the remote
    os.system(f"git fetch origin {branch_name}")

    # Reset the local branch to match the remote branch, keeping local changes
    os.system(f"git reset --keep origin/{branch_name}")

    # Checkout the latest changes from the remote, using theirs in case of conflicts
    os.system(f"git checkout -B {branch_name} origin/{branch_name}")
    