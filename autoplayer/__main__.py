
if __name__ == "__main__":
    import sys,os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    import confs.pip_packages 
    import confs.update_repo
    confs.update_repo.updating_some_directories(
        "main",
        
        "configs",
        "cel_configs",
    )