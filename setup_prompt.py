import tkinter as tk
from tkinter import messagebox
import time
import subprocess
import sys
import pygame
import json

# Initialize pygame mixer
pygame.mixer.init()

# Load the alarm sound
alarm_sound = pygame.mixer.Sound('gentle_alarm.mp3')

def submit():
    session_duration = session_entry.get()
    break_duration = break_entry.get()
    todo_list = todo_text.get("1.0", tk.END).strip().split('\n')
    if not session_duration or not break_duration or not todo_list:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    data = {
        'session_duration': session_duration,
        'break_duration': break_duration,
        'todo_list': todo_list
    }
    with open('config.json', 'w') as config_file:
        json.dump(data, config_file)
    root.destroy()

# Create the Tkinter window
root = tk.Tk()
root.title("Setup Prompt")
root.attributes('-topmost', True)  # Keep the window on top

# Add widgets
tk.Label(root, text="Enter session duration (minutes):").pack()
session_entry = tk.Entry(root)
session_entry.pack()

tk.Label(root, text="Enter break duration (minutes):").pack()
break_entry = tk.Entry(root)
break_entry.pack()

tk.Label(root, text="Enter to-do list (one item per line):").pack()
todo_text = tk.Text(root, height=10)
todo_text.pack()

tk.Button(root, text="Submit", command=submit).pack()

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

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
session_duration = float(config['session_duration']) * 60
break_duration = float(config['break_duration']) * 60
todo_list = config['todo_list']

# Main loop for alternating between session and break
todo_index = 0
while True:
    print(f"Work session for {session_duration // 60} minutes.")
    time.sleep(session_duration)

    # Get the current to-do item
    current_todo = todo_list[todo_index]
    todo_index = (todo_index + 1) % len(todo_list)

    # Launch break window
    process = subprocess.Popen([sys.executable, 'break_timer.py', str(break_duration), json.dumps([current_todo])])
    print(f"Break for {break_duration // 60} minutes.")

    process.wait()  # Wait for the break window process to complete
