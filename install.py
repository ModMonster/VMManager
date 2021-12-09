import os
import subprocess
import sys
import itertools
import time
import threading

# program
program = r'''from pynput.keyboard import Key, KeyCode, Listener, Controller
import os
from time import sleep
import math
import win32gui
from dadjokes import Dadjoke
from alive_progress import alive_bar
import subprocess

# config file layout
# 0 - vm path
# 1 - vmware path

# colors

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# vars

config = []
vms = []
vm_names = []
vm_display_names = []
running_vms = []

selected_vm = 0
vm_display_count = math.floor(os.get_terminal_size().columns / 28) - 1
scroll_buffer = 0
scroll_pos = 0

joke = ""

action = ""
manager_window = win32gui.GetForegroundWindow()

# functions

def print_scroll_bar(progress, total):
    size_l = ((os.get_terminal_size().columns / total) * progress) - 10
    size_r = (os.get_terminal_size().columns - size_l) - 11

    print("- " * math.floor(size_l / 2) + "██████████" + "- " * math.floor(size_r / 2))

def setup():
    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "w")

    # vm directory
    vm_dir = ""

    while (not os.path.isdir(vm_dir)):
        print("Type the path to your VMs directory.")
        vm_dir = input("> ")

        if (not os.path.isdir(vm_dir)):
            print("Invalid directory, try again.")
    
    # vmware path
    vmware_path = ""

    while (not os.path.isdir(vmware_path)):
        print("Type the path to your VMWare directory.")
        vmware_path = input("> ")

        if (not os.path.isdir(vmware_path)):
            print("Invalid directory, try again.")

    # write to file
    config_file.write(vm_dir + "\n" + vmware_path)

    config_file.close()

def get_vms():
    global config
    global vms
    global vm_names
    global running_vms

    # fullscreen + clear screen
    Controller().press(Key.f11)
    os.system("cls")

    # status message
    print("Locating virtual machines...")

    vm_folders = os.listdir(config[0])

    print(f"Scanning {len(vm_folders)} folders...")

    # get vmx files from folders
    with alive_bar(len(vm_folders)) as bar:
        for folder in vm_folders:
            path = config[0] + "\\" + folder
            folder_files = os.listdir(path) # get all files in vm folder
            bar() # update bar

            # loop through files looking for vmx
            for file in folder_files:
                # is extension vmx?
                file_split_ext = os.path.splitext(file)
                if (file_split_ext[1] == ".vmx"):
                    vms.append(f"{config[0]}\\{folder}\\{file}") # add to array
                    #print(f"Found virtual machine '{file}'") # status message
                    vm_names.append(file_split_ext[0])
    
    # get running vms
    running_vms = subprocess.check_output(config[1] + "\\vmrun.exe -T ws list").splitlines()[1:]

def get_vm_display_names():
    global vm_names
    global vm_display_names

    for vm in vm_names:
        if (len(vm) > 18):
            vm_display_names.append(vm[:16] + "..")
        else:
            vm_display_names.append(" " * (math.floor(9 - len(vm) / 2)) + vm + " " * math.ceil((9 - len(vm) / 2)))


def draw():
    global vm_names
    global vm_display_names
    global running_vms
    global scroll_buffer
    global scroll_pos
    global vm_display_count
    global selected_vm
    global joke

    vm_display_count = math.floor(os.get_terminal_size().columns / 28) - 1 # refresh display count

    os.system("cls")

    width = os.get_terminal_size().columns # get terminal width

    print("")
    print("VMManager v1.0.0 by ModMonster".center(width)) # info print

    if (len(vm_display_names) > 0):
        # get terminal size
        center_line = int(os.get_terminal_size().lines / 2 - 9)

        # newlines and counter / joke
        print('\n'*math.ceil((center_line / 3) * 2))

        if (joke == ""):
            print(f"{selected_vm + 1} / {len(vm_display_names)}".center(width))
        else:
            print(joke.center(width))
        
        print('\n'*math.floor(center_line / 3 - 1))

        # make array of boxes
        vm_boxes = []

        # crop it
        print_vms = vm_display_names[scroll_pos:vm_display_count + scroll_pos]

        # get list of running vm names
        running_vm_names = []

        for vm in running_vms:
            running_vm_names.append(str(vm).split("\\")[-1][:-5])

        # render it
        for vm in print_vms:
            if (vm_display_names.index(vm) == selected_vm):
                vm_boxes.append(f"""
            {bcolors.OKCYAN}╔════════════════════╗{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║ {vm} ║{bcolors.ENDC}
            {bcolors.OKCYAN}║ {"    (Running)     " if vm_names[vm_display_names.index(vm)] in running_vm_names else "                  "} ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
            {bcolors.OKCYAN}╚════════════════════╝{bcolors.ENDC}""")
            else:
                vm_boxes.append(f"""
            ┌────────────────────┐
            │                    │
            │                    │
            │                    │
            │                    │
            │ {vm} │
            │ {"    (Running)     " if vm_names[vm_display_names.index(vm)] in running_vm_names else "                  "} │
            │                    │
            │                    │
            │                    │
            └────────────────────┘""")

        boxes_split = [box.splitlines() for box in vm_boxes]

        # print it
        for l in zip(*boxes_split):
            print(*l)

        # scroll bar
        print("\n" * math.floor(center_line - 1))

        print_scroll_bar(selected_vm + 1, len(vms))
    else:
        # print newlines until halfway down
        center_line = int(os.get_terminal_size().lines / 2 - 4)
        print('\n'*center_line)

        print(f"No Virtual Machines found in '{config[0]}'".center(width))
        print(f"VMs must be made using VMWare and have a .vmx file to show here.".center(width))
        print(f"Press Escape to quit.".center(width))

        print('\n'*center_line)

def load_config():
    global config

    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "r")
    config = config_file.read().splitlines()
    config_file.close()

def validate_config():
    if (len(config) != 2 or not os.path.isdir(config[0]) or not os.path.isdir(config[1])):
        print("Invalid configuration file.")
        return True
    return False

def on_press(key):
    global action
    global selected_vm
    global vms
    global vm_display_count
    global scroll_buffer
    global scroll_pos
    global joke

    # ensure manager window is focused
    if (manager_window == win32gui.GetForegroundWindow()):
        if (key == Key.left and len(vms) > 0):
            if (selected_vm > 0):
                selected_vm -= 1
            else:
                selected_vm = len(vms) - 1
                scroll_buffer = -1
                scroll_pos = len(vms) - vm_display_count

            scroll_buffer += 1
            # manage scrolling
            if (scroll_buffer > vm_display_count - 1):
                scroll_pos -= 1
                scroll_buffer -= 1

            joke = "" # reset joke

            draw()
        elif (key == Key.right and len(vms) > 0):
            if (selected_vm < len(vms) - 1):
                selected_vm += 1
            else:
                selected_vm = 0
                scroll_buffer = vm_display_count
                scroll_pos = 0

            scroll_buffer -= 1
            # manage scrolling
            if (scroll_buffer < 0):
                scroll_pos += 1
                scroll_buffer += 1

            joke = "" # reset joke

            draw()
        elif (key == KeyCode.from_char("j")):
            joke = Dadjoke().joke # random joke
            draw()
        elif (key == Key.enter and len(vms) > 0):
            action = "start"
            return False
        elif (key == Key.esc):
            action = "exit"
            print("Quitting...")
            return False

def start_input():
    # start keyboard listener
    listener = Listener(
        on_press=on_press)
    listener.start()

def start_vm():
    print(f"Starting Virtual Machine '{vm_names[selected_vm]}'...")
    os.system(f'start {config[1]}\\vmware-kvm.exe "{vms[selected_vm]}"')

# start of actual code

# initial setup
if (not os.path.isfile(os.path.dirname(__file__) + "\\vmmanager.cfg")):
    setup()

load_config() # load config file and store in list

# validate config file
while validate_config():
    setup()
    load_config()

get_vms() # get list of vms from config file

if (len(vms) > 0):
    get_vm_display_names() # get display names by adding spaces / cutting off end of vm names
    start_input() # start input listener
    draw() # draw ui once

    scroll_buffer = vm_display_count - 1 # setup scroll buffer

    # main loop
    while True:
        if (action == "exit"):
            Controller().press(Key.f11)
            break
        elif (action == "start"):
            start_vm()
            break
        sleep(1)
else:
    start_input() # start input listener
    draw() # draw ui once

    while True:
        if (action == "exit"):
            Controller().press(Key.f11)
            break
        sleep(1)'''

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

    print("Installing dependencies...")

    # start loading thread
    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()

    # install dependencies
    i = 0
    for dependency in dependencies:
        i += 1 # increment progress
        progress = f"{i} / {len(dependencies)}" # update progress variable
        subprocess.run(f"pip install {dependency}", stdin=log_file, stdout=log_file, stderr=log_file) # run pip

    done = True

def install_vmmanager():
    global done
    global program
    global install_dir
    global progress

    print("Installing VMManager...")

    progress = "Moving main.py file"

    # start loading thread
    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()

    # install
    program_file = open(install_dir + "\\main.py", "w", encoding="utf-8")
    program_file.write(program)
    program_file.close()
    
    done = True

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

print("Welcome to the installer for VMManager v1.0.0!")

while not os.path.isdir(install_dir):
    if (install_dir != ""):
        print("Invalid directory, please try again.")

    print("Type the path to where you want VMManager to be installed.")
    install_dir = input("> ")

install_dependencies()

print("\n")
log_file.close()
done = False

install_vmmanager()

print("\n\nInstallation complete, press enter to exit.")
input("")