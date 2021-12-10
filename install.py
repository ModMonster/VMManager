import os
import subprocess
import sys
import itertools
import time
import threading
import importlib

# program
program = r'''Code to install'''
version = "1.0.0"

# vars

dependencies = [
    "pynput",
    "pywin32",
    "dadjokes",
    "alive-progress",
]
log_file = open("VMManagerInstaller.log", "w")

install_dir = ""
done = False
progress = ""

# functions

def install_dependencies():
    global log_file
    global progress
    global done

    progress = "Checking installed packages"

    # start loading thread
    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()

    # get installed packages
    installed_packages = [r.decode().split('==')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], stdin=log_file, stderr=log_file).split()]

    to_install = []
    # get packages that need to be installed
    for dependency in dependencies:
        if (not dependency in installed_packages):
            to_install.append(dependency)

    # install dependencies
    i = 0
    for dependency in to_install:
        time.sleep(1)
        i += 1 # increment progress
        progress = f"Installing packages - {i} / {len(to_install)}" # update progress variable
        subprocess.run(f"pip install {dependency}", stdin=log_file, stdout=log_file, stderr=log_file) # run pip

def install_vmmanager():
    global done
    global program
    global install_dir
    global progress

    print()
    progress = "Copying main.py file"

    # install
    program_file = open(install_dir + "\\main.py", "w", encoding="utf-8")
    program_file.write(program)
    program_file.close()

def animate():
    global done
    global progress

    for c in itertools.cycle(["|", "/", "-", "\\"]):
        if done:
            break
        sys.stdout.write(f"\r{progress} {c}")
        sys.stdout.flush()
        time.sleep(0.1)

# code

print(f"Welcome to the installer for VMManager v{version}!")

while not os.path.isdir(install_dir):
    if (install_dir != ""):
        print("Invalid directory, please try again.")

    print("Type the path to where you want VMManager to be installed.")
    install_dir = input("> ")

install_dependencies()

log_file.close()

install_vmmanager()

done = True

print("\n\nInstallation complete, press enter to exit.")
input("")