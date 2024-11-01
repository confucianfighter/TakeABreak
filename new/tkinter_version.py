import tkinter as tk
from tkinter import messagebox
import time
import json
import random
import toml
from settings_manager import settings
from playsound import playsound
import threading

class BreakApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Break Timer App")
        self.root.attributes('-topmost', True)  # Ensure the window stays on top
        self.settings_frame = tk.Frame(self.root)
        self.workflow_frame = tk.Frame(self.root)
        self.alarm_playing = False
        self.create_settings_frame()

    def create_settings_frame(self):
        self.settings_frame.pack(fill='both', expand=True)
        tk.Label(self.settings_frame, text="Enter session duration (minutes):").pack()
        self.session_entry = tk.Entry(self.settings_frame)
        self.session_entry.pack()

        tk.Label(self.settings_frame, text="Enter break duration (minutes):").pack()
        self.break_entry = tk.Entry(self.settings_frame)
        self.break_entry.pack()

        tk.Label(self.settings_frame, text="Enter to-do list (one item per line):").pack()
        self.todo_text = tk.Text(self.settings_frame, height=5)
        self.todo_text.pack()

        tk.Button(self.settings_frame, text="Start", command=self.start_session).pack()

        # Bind focus events
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.bind("<FocusIn>", self.on_focus_in)

    def start_session(self):
        try:
            session_duration = float(self.session_entry.get()) * 60
            break_duration = float(self.break_entry.get()) * 60
            todo_list = self.todo_text.get("1.0", tk.END).strip().split('\n')
            if not session_duration or not break_duration or not todo_list:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            settings.set('session_duration', session_duration)
            settings.set('break_duration', break_duration)
            settings.set('todo_list', todo_list)
            self.settings_frame.pack_forget()
            self.run_session(session_duration, break_duration, todo_list)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for session and break durations")

    def run_session(self, session_duration, break_duration, todo_list):
        self.root.after(int(session_duration * 1000), lambda: self.start_break(break_duration, todo_list))
        self.countdown(session_duration, "Session")

    def start_break(self, break_duration, todo_list):
        self.workflow_frame.pack(fill='both', expand=True)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.display_break_screen(break_duration, todo_list)

    def display_break_screen(self, break_duration, todo_list):
        self.workflow_frame.pack(fill='both', expand=True)
        tk.Label(self.workflow_frame, text="Break Time!").pack()
        tk.Label(self.workflow_frame, text="To-do List:").pack()
        for item in todo_list:
            tk.Label(self.workflow_frame, text=item).pack()
        self.countdown(break_duration, "Break")

    def countdown(self, duration, label):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            time_format = f"{int(minutes):02}:{int(seconds):02}"
            self.root.title(f"{label} - Time Remaining: {time_format}")
            self.root.after(1000, lambda: self.countdown(duration - 1, label))
        else:
            if label == "Break":
                self.end_break()

    def end_break(self):
        self.workflow_frame.pack_forget()
        self.root.attributes('-fullscreen', False)
        self.root.attributes('-topmost', True)  # Keep settings on top
        self.settings_frame.pack(fill='both', expand=True)

    def on_focus_out(self, event):
        if not self.alarm_playing:
            self.alarm_playing = True
            threading.Thread(target=self.play_alarm).start()

    def on_focus_in(self, event):
        self.alarm_playing = False

    def play_alarm(self):
        while self.alarm_playing:
            playsound('gentle_alarm.mp3')

if __name__ == "__main__":
    root = tk.Tk()
    app = BreakApp(root)
    root.mainloop()