from pynput.keyboard import Key, Listener, Controller
import os
from time import sleep
import shutil
import math

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

selected_vm = 0
action = ""

# functions

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

    # fullscreen + clear screen
    Controller().press(Key.f11)
    os.system("cls")

    # status message
    print("Locating virtual machines...")

    vm_folders = os.listdir(config[0])

    print(f"Found {len(vm_folders)} folders...")

    # get vmx files from folders
    for folder in vm_folders:
        path = config[0] + "\\" + folder
        folder_files = os.listdir(path) # get all files in vm folder

        # loop through files looking for vmx
        for file in folder_files:
            # is extension vmx?
            file_split_ext = os.path.splitext(file)
            if (file_split_ext[1] == ".vmx"):
                vms.append(f"{config[0]}\\{folder}\\{file}") # add to array
                print(f"Found virtual machine '{file}'") # status message
                vm_names.append(file_split_ext[0])

def get_vm_display_names():
    global vm_names
    global vm_display_names

    for vm in vm_names:
        if (len(vm) > 18):
            vm_display_names.append(vm[:16] + "..")
        else:
            vm_display_names.append(" " * (math.floor(9 - len(vm) / 2)) + vm + " " * math.ceil((9 - len(vm) / 2)))


def draw():
    global vm_display_names
    os.system("cls")

    width = os.get_terminal_size().columns # get terminal width

    print("")
    print("VMManager v1.0.0 by ModMonster".center(width)) # info print

    # print newlines until halfway down
    center_line = int(shutil.get_terminal_size().lines / 2 - 9)
    print('\n'*center_line)
    
    # make array of boxes
    vm_boxes = []

    # crop it
    print_vms = vm_display_names[selected_vm:math.floor(shutil.get_terminal_size().columns / 27) - 1 + selected_vm]

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
        {bcolors.OKCYAN}║                    ║{bcolors.ENDC}
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
        │                    │
        │                    │
        │                    │
        │                    │
        └────────────────────┘""")

    boxes_split = [box.splitlines() for box in vm_boxes]

    # print it
    for l in zip(*boxes_split):
        print(*l)

def load_config():
    global config

    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "r")
    config = config_file.read().splitlines()
    config_file.close()

def on_press(key):
    global action
    global selected_vm
    global vms

    if (key == Key.left):
        if (selected_vm > 0):
            selected_vm -= 1
        else:
            selected_vm = len(vms) - 1

        draw()
    elif (key == Key.right):
        if (selected_vm < len(vms) - 1):
            selected_vm += 1
        else:
            selected_vm = 0

        draw()
    elif (key == Key.enter):
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

if (not os.path.isfile(os.path.dirname(__file__) + "\\vmmanager.cfg")):
    setup()

load_config() # load config file and store in list
get_vms() # get list of vms from config file
get_vm_display_names() # get display names by adding spaces / cutting off end of vm names
start_input() # start input listener
draw() # draw ui once

# main loop
while True:
    if (action == "exit"):
        Controller().press(Key.f11)
        break
    elif (action == "start"):
        start_vm()
        break
    sleep(1)