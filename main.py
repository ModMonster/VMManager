from pynput.keyboard import Key, KeyCode, Listener, Controller
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
# 2 - selected vm color

# colors

class colors:
    RED = '\033[31;40m'
    GREEN = '\033[32;40m'
    YELLOW = '\033[33;40m'
    BLUE = '\033[34;40m'
    MAGENTA = '\033[35;40m'
    CYAN = '\033[36;40m'
    SELOPTION = "\033[47;30m"
    ENDC = '\033[0m'

color_names = [
    "RED",
    "GREEN",
    "YELLOW",
    "BLUE",
    "MAGENTA",
    "CYAN"
]

# settings functions
def reset_config():
    os.remove(os.path.dirname(__file__) + "\\vmmanager.cfg")
    os.remove(os.path.dirname(__file__) + "\\favourites.cfg")
    print("\nConfiguration files removed, restart VMManager to regenerate.")

def change_color():
    global color_names
    global config
    global color

    color_index = color_names.index(config[2])

    print(color_index == len(color_names))

    if (color_index == len(color_names) - 1):
        color_index = 0
    else:
        color_index += 1

    write_config(2, color_names[color_index])

    load_config()
    get_colors()

    draw_settings()

def exit_settings():
    global settings_open
    settings_open = False
    draw()

# vars

config = []
vms = []
vm_names = []
vm_display_names = []
favourite_vms = []
running_vms = []
running_vm_names = []

selected_vm = 0
vm_display_count = math.floor(os.get_terminal_size().columns / 29) - 1
scroll_buffer = 0
scroll_pos = 0
color = colors.ENDC

settings_selection = 0
settings_open = False
settings_options = []
settings_functions = [
    reset_config,
    change_color,
    exit_settings,
]

selected_option = 0

joke = ""

action = ""
manager_window = win32gui.GetForegroundWindow()

# functions

def print_scroll_bar(progress, total):
    size_l = ((os.get_terminal_size().columns / total) * progress) - 10
    size_r = (os.get_terminal_size().columns - size_l) - 11

    print("- " * math.floor(size_l / 2) + "██████████" + "- " * math.floor(size_r / 2))

def write_config(line, option):
    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "r")
    config_lines = config_file.readlines()

    config_lines[line] = option

    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "w")
    config_file.writelines(config_lines)
    config_file.close()

def setup():
    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "w")

    # vm directory
    vm_dir = ""

    while (not os.path.isdir(vm_dir)):
        print("Type the path to your VMs directory.")
        vm_dir = input("> ")
        
        # set default path if blank
        if (vm_dir == ""):
            vm_dir = os.path.expanduser("~\\Documents\\Virtual Machines\\")
        
        # make sure directory is valid
        if (not os.path.isdir(vm_dir)):
            print("Invalid directory, try again.")
    
    # vmware path
    vmware_path = ""

    while (not os.path.isdir(vmware_path) or not os.path.isfile(vmware_path + "\\vmrun.exe") or not os.path.isfile(vmware_path + "\\vmware-kvm.exe")):
        print("Type the path to your VMWare directory.")
        vmware_path = input("> ")

        # set default path if blank
        if (vmware_path == ""):
            vmware_path = "C:\\Program Files (x86)\\VMware\\VMware Player"

        # make sure directory is valid
        if (not os.path.isdir(vmware_path)):
            print("Invalid directory, try again.")
            
        # make sure directory contains needed files
        if (not os.path.isfile(vmware_path + "\\vmrun.exe") or not os.path.isfile(vmware_path + "\\vmware-kvm.exe")):
            print("Directory is valid, but doesn't contain a valid VMWare installation.")

    # write to file
    config_file.write(vm_dir + "\n" + vmware_path + "\n" + "CYAN")

    config_file.close()

def get_favourites():
    global favourite_vms
    global vm_names
    
    # read favourites file
    favourites_file = open(os.path.dirname(__file__) + "\\favourites.cfg", "r")
    favourite_vms = favourites_file.read().splitlines()
    favourites_file.close()

    # sort vms as favourite
    for vm in favourite_vms:
        vms.remove(vm)
        vms.insert(0, vm)
        vm_names.remove(os.path.splitext(vm.split("\\")[-1])[0])
        vm_names.insert(0, os.path.splitext(vm.split("\\")[-1])[0])

def favourite_vm(vm):
    global favourite_vms
    global vms
    global vm_display_names
    global vm_names
    global favourite_vms

    if (vm in favourite_vms):
        favourite_vms.remove(vm) # remove from list
    else:
        favourite_vms.append(vm) # add to list

    favourites_file = open(os.path.dirname(__file__) + "\\favourites.cfg", "w")
    favourites_file.write("\n".join(favourite_vms))
    favourites_file.close()

    vms = []
    vm_display_names = []
    vm_names = []
    favourite_vms = []

    get_vms()
    get_favourites()
    get_vm_display_names()
    draw()

def get_vms():
    global config
    global vms
    global vm_names
    global running_vms

    # clear screen
    os.system("cls")

    # status message
    print("Locating virtual machines...")

    vm_folders = os.listdir(config[0])

    print(f"Scanning {len(vm_folders)} folders...")

    # get vmx files from folders
    with alive_bar(len(vm_folders)) as bar:
        for folder in vm_folders:
            path = config[0] + "\\" + folder

            # make sure path is a folder
            if (os.path.isdir(path)):
                folder_files = os.listdir(path) # get all files in vm folder
                bar() # update bar

                # loop through files looking for vmx
                for file in folder_files:
                    # is extension vmx?
                    file_split_ext = os.path.splitext(file)
                    if (file_split_ext[1] == ".vmx"):
                        vms.append(f"{config[0]}\\{folder}\\{file}") # add to array
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
    global color
    global selected_option
    global running_vm_names
    global favourite_vms

    vm_display_count = math.floor(os.get_terminal_size().columns / 29) - 1 # refresh display count

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
        for vm in running_vms:
            running_vm_names.append(str(vm).split("\\")[-1][:-5])

        # render it
        for vm in print_vms:
            if (vm_display_names.index(vm) == selected_vm and vm_names[vm_display_names.index(vm)] in running_vm_names):
                vm_boxes.append(f"""
            {color}╔════════════════════╗{colors.ENDC}
            {color}║                  {"*" if vms[vm_display_names.index(vm)] in favourite_vms else " "} ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║ {vm} ║{colors.ENDC}
            {color}║ {"    (Running)     " if vm_names[vm_display_names.index(vm)] in running_vm_names else "                  "} ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}╠════════════════════╣{colors.ENDC}
            {color}║ {colors.SELOPTION if selected_option == 0 else colors.ENDC}       Show       {color} ║{colors.ENDC}
            {color}║ {colors.SELOPTION if selected_option == 1 else colors.ENDC}     Shutdown     {color} ║{colors.ENDC}
            {color}║ {colors.SELOPTION if selected_option == 2 else colors.ENDC}      Reboot      {color} ║{colors.ENDC}
            {color}║ {colors.SELOPTION if selected_option == 3 else colors.ENDC}     Suspend      {color} ║{colors.ENDC}
            {color}║ {colors.SELOPTION if selected_option == 4 else colors.ENDC}  Force Shutdown  {color} ║{colors.ENDC}
            {color}╚════════════════════╝{colors.ENDC}""")
            elif (vm_display_names.index(vm) == selected_vm):
                vm_boxes.append(f"""
            {color}╔════════════════════╗{colors.ENDC}
            {color}║                  {"*" if vms[vm_display_names.index(vm)] in favourite_vms else " "} ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║ {vm} ║{colors.ENDC}
            {color}║ {"    (Running)     " if vm_names[vm_display_names.index(vm)] in running_vm_names else "                  "} ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}║                    ║{colors.ENDC}
            {color}╚════════════════════╝{colors.ENDC}
            {color}                      {colors.ENDC}
            {color}                      {colors.ENDC}
            {color}                      {colors.ENDC}
            {color}                      {colors.ENDC}
            {color}                      {colors.ENDC}
            {color}                      {colors.ENDC}""")
            else:
                vm_boxes.append(f"""
            ┌────────────────────┐
            │                  {"*" if vms[vm_display_names.index(vm)] in favourite_vms else " "} │
            │                    │
            │                    │
            │                    │
            │ {vm} │
            │ {"    (Running)     " if vm_names[vm_display_names.index(vm)] in running_vm_names else "                  "} │
            │                    │
            │                    │
            │                    │
            └────────────────────┘
                                  
                                  
                                  
                                  
                                  
                                  """)

        # print it
        for l in zip(*[box.splitlines() for box in vm_boxes]):
            print(*l)

        # print controls
        print('\n'*math.floor(center_line / 3 - 3))

        print(f"← left    → right{'    ↑ up    ↓ down' if vm_names[selected_vm] in running_vm_names else ''}    'ESC' exit    'ENTER' start    {''''SPACE' unfavourite''' if vms[selected_vm] in favourite_vms else ''''SPACE' favourite'''}    'S' settings".center(width))
        
        print('\n'*math.ceil((center_line / 3) * 2 - 6))

        # scroll bar

        print_scroll_bar(selected_vm + 1, len(vms))
    else:
        # print newlines until halfway down
        center_line = int(os.get_terminal_size().lines / 2 - 4)
        print('\n'*center_line)

        print(f"No Virtual Machines found in '{config[0]}'".center(width))
        print(f"VMs must be made using VMWare and have a .vmx file to show here.".center(width))
        print(f"Press Escape to quit.".center(width))

        print('\n'*center_line)

def draw_settings():
    global settings_selection
    global settings_options
    global config

    settings_options = [
        "Reset configuration",
        f"Change color ({config[2]})",
        "Exit",
    ]

    os.system("cls")

    width = os.get_terminal_size().columns # get terminal width
    height = os.get_terminal_size().lines # get terminal height

    print("")
    print("Settings".center(width)) # info print
    print("")

    print("\n" * math.ceil(height / 2 - len(settings_options) - 3))

    print("────────────────────────────────────────".center(width))

    # draw options list
    for option in settings_options:
        if (settings_options.index(option) == settings_selection):
            print(" " * (math.floor(width / 2) - 18) + colors.SELOPTION + "> " + option + colors.ENDC)
        else:
            print(" " * (math.floor(width / 2) - 18) + "  " + option)

    print("────────────────────────────────────────".center(width))

    print("\n" * math.floor(height / 2 - len(settings_options) - 3))

def load_config():
    global config
    global color

    config_file = open(os.path.dirname(__file__) + "\\vmmanager.cfg", "r")
    config = config_file.read().splitlines()
    config_file.close()

def validate_config():
    if (len(config) != 3 or not os.path.isdir(config[0]) or not os.path.isdir(config[1])):
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
    global settings_open
    global settings_options
    global settings_selection
    global settings_functions
    global selected_option
    global running_vm_names

    # ensure manager window is focused
    if (manager_window == win32gui.GetForegroundWindow()):
        # in settings?
        if (settings_open):
            if (key == Key.up):
                if (settings_selection > 0):
                    settings_selection -= 1
                else:
                    settings_selection = len(settings_options) - 1
                
                draw_settings()
            elif (key == Key.down):
                if (settings_selection < len(settings_options) - 1):
                    settings_selection += 1
                else:
                    settings_selection = 0

                draw_settings()
            elif (key == Key.enter):
                settings_functions[settings_selection]()
            elif (key == KeyCode.from_char("s") or key == Key.esc):
                settings_open = False
                draw()
        else:
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
            elif (key == Key.up):
                if (vm_names[selected_vm] in running_vm_names):
                    if (selected_option > 0):
                        selected_option -= 1
                    else:
                        selected_option = 4

                    joke = "" # reset joke

                    draw()
            elif (key == Key.down):
                if (vm_names[selected_vm] in running_vm_names):
                    if (selected_option < 4):
                        selected_option += 1
                    else:
                        selected_option = 0

                    joke = "" # reset joke

                    draw()
            elif (key == Key.space):
                favourite_vm(vms[selected_vm])
            elif (key == KeyCode.from_char("j")):
                joke = Dadjoke().joke # random joke
                draw()
            elif (key == KeyCode.from_char("s")):
                settings_open = True
                joke = "" # reset joke
                draw_settings()
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
    global running_vm_names
    global selected_option

    # check running vm options
    if (vm_names[selected_vm] in running_vm_names):
        if (selected_option == 0):
            print(f"Showing virtual machine '{vm_names[selected_vm]}'...")
            os.system(f'start {config[1]}\\vmware-kvm.exe "{vms[selected_vm]}"')
        elif (selected_option == 1):
            print(f"Shutting down virtual machine '{vm_names[selected_vm]}'...")
            os.system(f'start {config[1]}\\vmware-kvm.exe --power-off "{vms[selected_vm]}"')
        elif (selected_option == 2):
            print(f"Rebooting virtual machine '{vm_names[selected_vm]}'...")
            os.system(f'start {config[1]}\\vmware-kvm.exe --reset "{vms[selected_vm]}"')
        elif (selected_option == 3):
            print(f"Suspending virtual machine '{vm_names[selected_vm]}'...")
            os.system(f'start {config[1]}\\vmware-kvm.exe --suspend "{vms[selected_vm]}"')
        elif (selected_option == 4):
            print(f"Forcing virtual machine '{vm_names[selected_vm]}' to shut down...")
            os.system(f'start {config[1]}\\vmware-kvm.exe --power-off=hard "{vms[selected_vm]}"')
    else:
        print(f"Starting virtual machine '{vm_names[selected_vm]}'...")
        os.system(f'start {config[1]}\\vmware-kvm.exe "{vms[selected_vm]}"')

def get_colors():
    global color
    global config

    # set color
    if (config[2] == "RED"):
        color = colors.RED
    elif (config[2] == "GREEN"):
        color = colors.GREEN
    elif (config[2] == "YELLOW"):
        color = colors.YELLOW
    elif (config[2] == "BLUE"):
        color = colors.BLUE
    elif (config[2] == "MAGENTA"):
        color = colors.MAGENTA
    elif (config[2] == "CYAN"):
        color = colors.CYAN

# start of actual code

# initial setup
if (not os.path.isfile(os.path.dirname(__file__) + "\\vmmanager.cfg")):
    setup()

load_config() # load config file and store in list

# validate config file
while validate_config():
    setup()
    load_config()

Controller().press(Key.f11) # fullscreen
get_vms() # get list of vms from config file
get_favourites() # get list of favourite vms from favourite file
get_colors() # set primary color

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
        sleep(1)