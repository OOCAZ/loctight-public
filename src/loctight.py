#! python3
# Written by OOCAZ (Zac Poorman)
# LOCTight - A simple timer to keep your computer active and open.

import time
import subprocess
import ctypes
import threading
import pyautogui
from sys import platform
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import darkdetect
import os
import sys


if sys.platform.startswith("linux"):
    if "DISPLAY" not in os.environ:
        print("Error: No DISPLAY environment variable set. GUI features will not work.")
        sys.exit(1)


def jiggle(x, checks):
    a = 0
    while a < x and timer_running[0]:
        b = 0
        while b < 6 and timer_running[0]:
            pyautogui.moveRel(0, 1, duration=0.001)
            time.sleep(10)
            b += 1
        a += 1
    if checks == 0 and timer_running[0]:
        if platform == "linux" or platform == "linux2":
            subprocess.call(
                "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend",
                shell=True,
            )
        elif platform == "darwin":
            subprocess.call(
                "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend",
                shell=True,
            )
        else:
            ctypes.windll.user32.LockWorkStation()


paused = [False]


def pause_timer():
    if timer_running[0]:
        paused[0] = not paused[0]
        if paused[0]:
            pause_button.config(text="Resume Timer")
        else:
            pause_button.config(text="Pause Timer")


def countdown(variable, checks):
    minutes = variable
    seconds = 0
    while minutes > 0 and timer_running[0]:
        seconds = 59
        update_time_label(minutes - 1, seconds)
        pyautogui.moveRel(0, 1, duration=0.001)
        while seconds >= 0 and timer_running[0]:
            while paused[0] and timer_running[0]:
                time.sleep(0.1)
            update_time_label(minutes - 1, seconds)
            time.sleep(1)
            seconds -= 1
        minutes -= 1
    if timer_running[0]:
        update_time_label(0, 0)
        # Check the IntVar at the end, not at the start! That way user can change mind
        if checks.get() == 0:
            if platform == "linux" or platform == "linux2":
                subprocess.call(
                    "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend",
                    shell=True,
                )
            elif platform == "darwin":
                subprocess.call(
                    "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend",
                    shell=True,
                )
            else:
                ctypes.windll.user32.LockWorkStation()
    timer_running[0] = False
    paused[0] = False
    pause_button.config(text="Pause Timer", state=tb.DISABLED)
    enable_buttons()


def update_time_label(m, s):
    # Only update if timer is running or resetting to 00:00
    if timer_running[0] or (m == 0 and s == 0):
        time_str = f"Time Left: {m:02}:{s:02}"
        label3.config(text=time_str)


def start_timer(duration):
    if not timer_running[0]:
        timer_running[0] = True
        paused[0] = False
        pause_button.config(text="Pause Timer", state=tb.NORMAL)
        disable_buttons()
        t = threading.Thread(
            target=countdown,
            args=(duration, checks),
            daemon=True,
        )
        t.start()


def cancel_timer():
    timer_running[0] = False
    paused[0] = False
    pause_button.config(text="Pause Timer", state=tb.DISABLED)
    enable_buttons()
    update_time_label(0, 0)
    entry.delete(0, tb.END)  # Clear the entry field when cancelling


def short():
    start_timer(30)


def longs():
    start_timer(60)


def custom():
    try:
        Ctime = int(entry.get())
        if Ctime <= 0:
            raise ValueError
        start_timer(Ctime)
    except ValueError:
        messagebox.showerror(
            "Invalid Input", "Please enter a positive integer for minutes."
        )


def disable_buttons():
    button1.config(state=tb.DISABLED)
    button2.config(state=tb.DISABLED)
    button3.config(state=tb.DISABLED)
    # Remove start_button if not present
    cancel_button.config(state=tb.NORMAL)
    pause_button.config(state=tb.NORMAL)


def enable_buttons():
    button1.config(state=tb.NORMAL)
    button2.config(state=tb.NORMAL)
    button3.config(state=tb.NORMAL)
    # Remove start_button if not present
    cancel_button.config(state=tb.DISABLED)
    pause_button.config(state=tb.DISABLED)


theme = "darkly" if darkdetect.isDark() else "flatly"
window = tb.Window(themename=theme)  # "auto" matches system light/dark mode

window.title("LOCTight")
window.geometry("500x400")
window.resizable(True, True)

main_frame = tb.Frame(window, padding=30)
main_frame.pack(expand=True, fill="both")

label1 = tb.Label(
    main_frame,
    text="Select a time to keep your computer active and open.\nCheck the box to leave unlocked after time ends.",
    anchor="center",
    justify="center",
    wraplength=400,
)
label1.pack(pady=(0, 20))

button_frame = tb.Frame(main_frame)
button_frame.pack(pady=5)

button1 = tb.Button(button_frame, text="30 Minute Timer", command=short)
button1.grid(row=0, column=0, padx=10)

button2 = tb.Button(button_frame, text="1 Hour Timer", command=longs)
button2.grid(row=0, column=1, padx=10)

custom_frame = tb.Frame(main_frame)
custom_frame.pack(pady=10)

entry = tb.Entry(custom_frame, width=10)
entry.grid(row=0, column=0, padx=(0, 10))
button3 = tb.Button(custom_frame, text="Custom (min)", command=custom)
button3.grid(row=0, column=1)

checks = tb.IntVar(value=0)

chkbtn = tb.Checkbutton(
    main_frame,
    text="Leave Computer Unlocked",
    variable=checks,
    onvalue=1,
    offvalue=0,
)
chkbtn.pack(pady=10)

label3 = tb.Label(
    main_frame, text="Time Left: 00:00", anchor="center", relief="groove", width=25
)
label3.pack(pady=10)

action_frame = tb.Frame(main_frame)
action_frame.pack(pady=10)

pause_button = tb.Button(
    action_frame, text="Pause Timer", command=pause_timer, state=tb.DISABLED
)
pause_button.grid(row=0, column=0, padx=10)

cancel_button = tb.Button(
    action_frame, text="Cancel Timer", command=cancel_timer, state=tb.DISABLED
)
cancel_button.grid(row=0, column=1, padx=10)

timer_running = [False]
paused = [False]

window.mainloop()
