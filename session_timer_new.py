import tkinter as tk
import win32gui 
import subprocess
import sys
import pygame
import json
from settings_manager import settings
import time
import win32event
import win32api
import winerror
    
# Create a mutex to prevent multiple instances of the app from running
mutex = win32event.CreateMutex(None, False, "take_a_break")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("Another instance of this app is already running. Exiting.")
    sys.exit()

# Initialize pygame mixer for playing the alarm sound
pygame.mixer.init()

# Load the alarm sound
alarm_sound = pygame.mixer.Sound('gentle_alarm.mp3')

# Create the Tkinter window with a dark theme
root = tk.Tk()
root.title("Setup Prompt")
root.attributes('-topmost', True)  # Keep the window on top
root.configure(bg='#2E2E2E')  # Set the background color to dark

# Load existing settings
session_duration = settings.get('session_duration', 25.0)
break_duration = settings.get('break_duration', 5.0)
todo_list = settings.get('todo_list', [])

def submit():
    try:
        session_duration = float(session_entry.get())
        break_duration = float(break_entry.get())
        todo_list = [entry.get() for entry in todo_entries if entry.get().strip()]
        if not session_duration or not break_duration or not todo_list:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        settings.set('session_duration', session_duration)
        settings.set('break_duration', break_duration)
        settings.set('todo_list', todo_list)
        root.destroy()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for session and break durations")

# Add widgets and populate fields if settings exist
tk.Label(root, text="Enter session duration (minutes):", bg='#2E2E2E', fg='#FFFFFF', font=("Arial", 12)).pack()
session_entry = tk.Entry(root, bg='#3E3E3E', fg='#FFFFFF', insertbackground='#FFFFFF', font=("Arial", 12))
session_entry.insert(0, str(session_duration))
session_entry.pack()

tk.Label(root, text="Enter break duration (minutes):", bg='#2E2E2E', fg='#FFFFFF', font=("Arial", 12)).pack()
break_entry = tk.Entry(root, bg='#3E3E3E', fg='#FFFFFF', insertbackground='#FFFFFF', font=("Arial", 12))
break_entry.insert(0, str(break_duration))
break_entry.pack()

tk.Label(root, text="Enter to-do list items:", bg='#2E2E2E', fg='#FFFFFF', font=("Arial", 12)).pack()

# Frame to hold all to-do entries
todo_frame = tk.Frame(root, bg='#2E2E2E')
todo_frame.pack(fill='both', expand=True)

todo_entries = []

def create_todo_entry(item_text=""):
    frame = tk.Frame(todo_frame, bg='#3E3E3E')
    frame.pack(fill='x', pady=2)

    entry = tk.Entry(frame, bg='#3E3E3E', fg='#FFFFFF', insertbackground='#FFFFFF', font=("Arial", 12))
    entry.insert(0, item_text)
    entry.pack(side='left', fill='x', expand=True)

    remove_button = tk.Button(frame, text="Remove", command=lambda: remove_todo_entry(frame, entry), bg='#4E4E4E', fg='#FFFFFF', font=("Arial", 12))
    remove_button.pack(side='right')

    todo_entries.append(entry)

def remove_todo_entry(frame, entry):
    todo_entries.remove(entry)
    frame.destroy()

# Populate existing to-do list items
for item in todo_list:
    create_todo_entry(item)

# Button to add new to-do entry
tk.Button(root, text="Add Item", command=lambda: create_todo_entry(), bg='#4E4E4E', fg='#FFFFFF', font=("Arial", 12)).pack()

tk.Button(root, text="Submit", command=submit, bg='#4E4E4E', fg='#FFFFFF', font=("Arial", 12)).pack()

# Alarm control
alarm_playing = False

def on_focus_out(event):
    global alarm_playing
    if not alarm_playing:
        print("Setup window lost focus, please bring it to the front.")
        alarm_sound.play(loops=-1)
        alarm_playing = True

def on_focus_in(event):
    global alarm_playing
    if alarm_playing:
        alarm_sound.stop()
        alarm_playing = False

# Bind focus events
root.bind("<FocusOut>", on_focus_out)
root.bind("<FocusIn>", on_focus_in)

# Run the Tkinter main loop
root.mainloop()

# Load configuration from settings
session_duration = settings.get('session_duration') * 60
break_duration = settings.get('break_duration') * 60
todo_list = settings.get('todo_list')

# Main loop for alternating between session and break
todo_index = 0
while True:
    countdown = session_duration
    print(f"Work session for {session_duration // 60} minutes.")
    while countdown > 0:
        # clear the screen
        print('\033c', end='')
        seconds = countdown % 60
        print(f"Time remaining: {countdown // 60} minutes, {seconds} seconds.")
        time.sleep(1)
        countdown -= 1

    # Get the current to-do item
    current_todo = todo_list[todo_index]
    todo_index = (todo_index + 1) % len(todo_list)

    # Launch break window
    process = subprocess.Popen([sys.executable, 'break_timer.py', str(break_duration), json.dumps([current_todo])])
    print(f"Break for {break_duration // 60} minutes.")

    process.wait()  # Wait for the break window process to complete
