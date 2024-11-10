import tkinter as tk
from tkinter import messagebox
import time
import json
import random
import toml
from settings_manager import settings
from playsound import playsound
import threading
import pygame
import subprocess
import win32api
import win32event
import winerror
from inspirational_quote import get_inspirational_quote
import os

# change cwd to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
testing = True


def load_writing_prompts():
    with open('writing_prompts.toml', 'r') as file:
        data = toml.load(file)
    return data['prompts']

def load_mindfulness_reminders():
    data = None
    # print cwd
    print(os.getcwd())
    with open('mindfulness_reminders.toml', 'r') as file:
        data = toml.load(file)
    print(random.choice(data['mindfulness_reminders']))
    return data['mindfulness_reminders']

class BreakApp:
    
    def __init__(self, root):
        if not testing:
            self.enforce_single_instance()
        self.mindfulness_reminders = load_mindfulness_reminders()
        self.snooze_duration = 1  # Snooze duration in minutes
        self.break_duration = settings.get('break_duration', 5.0)
        self.session_duration = settings.get('session_duration', 25.0)
        self.todo_list = settings.get('todo_list', [])
        self.num_mindfulness_reminders = int(settings.get('num_mindfulness_reminders', 3))  # Ensure it's retrieved as an integer
        self.pre_break_warning_duration_minutes = settings.get('pre_break_warning_duration_minutes', .25)
        pygame.mixer.init()
        self.root = root
        self.root.title("Break Timer App")
        self.root.attributes('-topmost', True)  # Ensure the window stays on top
        self.settings_frame = tk.Frame(self.root)
        self.workflow_frame = tk.Frame(self.root)
        self.alarm_playing = False
        self.create_settings_frame()
        
    def enforce_single_instance(self):
        # Create a mutex to prevent multiple instances of the app from running
        mutex = win32event.CreateMutex(None, False, "take_a_break")

        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            print("Another instance of this app is already running. Exiting.")
            sys.exit()

    def create_settings_frame(self):
        self.settings_frame.pack(fill='both', expand=True)

        # Load existing settings
        
        # Define font and color settings for the dark theme
        font_settings = ("Arial", 36)  # 3 times bigger than typical size
        bg_color = '#2E2E2E'  # Dark background
        fg_color = '#FFFFFF'  # White text

        self.settings_frame.configure(bg=bg_color)

        tk.Label(self.settings_frame, text="Enter session duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.session_entry = tk.Entry(self.settings_frame, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.session_entry.insert(0, str(self.session_duration))  # Convert seconds back to minutes
        self.session_entry.pack()

        tk.Label(self.settings_frame, text="Enter break duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.break_entry = tk.Entry(self.settings_frame, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.break_entry.insert(0, str(self.break_duration))  # Convert seconds back to minutes
        self.break_entry.pack()

        tk.Label(self.settings_frame, text="Enter to-do list (one item per line):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.todo_text = tk.Text(self.settings_frame, height=5, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.todo_text.insert("1.0", "\n".join(self.todo_list))
        self.todo_text.pack()

        tk.Label(self.settings_frame, text="Enter number of mindfulness reminders:", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.reminders_entry = tk.Entry(self.settings_frame, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.reminders_entry.insert(0, str(self.num_mindfulness_reminders))
        self.reminders_entry.pack()

        tk.Label(self.settings_frame, text="Enter pre-break warning duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.pre_break_warning_entry = tk.Entry(self.settings_frame, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.pre_break_warning_entry.insert(0, str(self.pre_break_warning_duration_minutes))
        self.pre_break_warning_entry.pack()

        tk.Button(self.settings_frame, text="Start", command=self.on_submit_settings, font=font_settings, bg='#4E4E4E', fg=fg_color).pack()

        # Bind focus events
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.bind("<FocusIn>", self.on_focus_in)
    # we need to refactor so that if it's a snooze, we can use 0 mindfulness reminders and have a different break duration
    def on_submit_settings(self):
        try:
            self.session_duration = float(self.session_entry.get())
            self.break_duration = float(self.break_entry.get())
            self.todo_list = self.todo_text.get("1.0", tk.END).strip().split('\n')
            self.num_mindfulness_reminders = int(self.reminders_entry.get())
            self.pre_break_warning_duration_minutes = float(self.pre_break_warning_entry.get())
            if not self.session_duration or not self.break_duration or not self.todo_list or self.num_mindfulness_reminders <= 0:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            settings.set('session_duration', self.session_duration)
            settings.set('break_duration', self.break_duration)
            settings.set('todo_list', self.todo_list)
            settings.set('num_mindfulness_reminders', self.num_mindfulness_reminders)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for session and break durations")
        self.settings_frame.pack_forget()
        self.run_session(self.session_duration, self.break_duration, self.todo_list, self.num_mindfulness_reminders)
    
    def run_session(self, session_duration, break_duration, todo_list, num_mindfulness_reminders, is_snooze=False):
        self.alarm_playing = False  # Disables the alarm
        self.root.iconify() # minimizes the window
        self.root.attributes('-topmost', False) # sets topmost to false
        if not is_snooze:
            self.schedule_mindfulness_reminders(session_duration, num_mindfulness_reminders)
            self.schedule_pre_break_warning(self.pre_break_warning_duration_minutes)
        self.root.after(int(session_duration * 60 * 1000), lambda: self.start_break(break_duration, todo_list))
        self.countdown(session_duration, "Session")

    def schedule_pre_break_warning(self, pre_break_warning_duration_minutes):
        # calculate minutes as session duration - pre break warning
        minutes = self.session_duration - pre_break_warning_duration_minutes
        print(f"Scheduling pre-break warning for {minutes} minutes")
        mindfulness_reminder = f"Break will commence in {minutes} minutes. Tune in with your breathing and start working on a stopping point."
        self.root.after(int(minutes * 60 * 1000), self.play_mindfulness_bell_and_reminder, mindfulness_reminder)
    

    def start_break(self, break_duration, todo_list):
        self.alarm_playing = True
        # prepare a gentle "it's break time" message
        break_time_message = "It is now break time. Take a moment to stretch, breathe, and reflect."
        # play mindfulness bell and reminder
        # schedule break screen for 10 seconds from now
        
        
        self.root.after(8000, self.start_break_sequence(break_duration, todo_list))
        self.play_mindfulness_bell_and_reminder(break_time_message)

    def start_break_sequence(self, break_duration, todo_list):
        self.root.deiconify()  # Restore the window
        self.workflow_frame.pack(fill='both', expand=True)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.workflow_frame.configure(bg='black')  # Set background to black

        # Clear any existing widgets
        for widget in self.workflow_frame.winfo_children():
            widget.destroy()

        # Define font settings for large text
        font_settings = ("Arial", 48)  # Large font size

        # Load standard prompts
        standard_prompts = [
            "Enter a positive affirmation:",
            "Enter a statement of acceptance:",
            "Enter a statement of gratitude:"
        ]

        # Load writing prompts
        writing_prompts = load_writing_prompts()

        # Randomly replace two standard prompts with writing prompts
        for _ in range(2):
            index_to_replace = random.choice(range(len(standard_prompts)))
            random_prompt = random.choice(writing_prompts)
            standard_prompts[index_to_replace] = random_prompt

        # Start displaying prompts
        self.display_prompts(standard_prompts, break_duration, todo_list, font_settings)

    def display_prompts(self, prompts, break_duration, todo_list, font_settings, index=0):
        if index < len(prompts):
            # Clear any existing widgets
            for widget in self.workflow_frame.winfo_children():
                widget.destroy()

            # Display the current prompt with text wrapping
            prompt_label = tk.Label(
                self.workflow_frame,
                text=prompts[index],
                font=font_settings,
                bg='black',
                fg='white',
                wraplength=self.root.winfo_screenwidth() - 100  # Wrap text to fit within the screen width
            )
            prompt_label.pack(expand=True, pady=20)

            # Add an input field for the user to answer the prompt
            answer_entry = tk.Text(self.workflow_frame, height=5, font=("Arial", 24), bg='#3E3E3E', fg='white', insertbackground='white')
            answer_entry.pack(expand=True, pady=20)

            # Function to handle submission
            def submit_answer(event=None):
                self.next_prompt(prompts, break_duration, todo_list, font_settings, index, answer_entry)

            # Bind Ctrl+Enter to submit the answer
            answer_entry.bind('<Control-Return>', submit_answer)

            # Button to proceed to the next prompt
            next_button = tk.Button(self.workflow_frame, text="Next", command=submit_answer, font=("Arial", 24), bg='#4E4E4E', fg='white')
            next_button.pack(pady=20, fill='x', expand=True)

            # Snooze button
            snooze_button = tk.Button(self.workflow_frame, text="Snooze", command=lambda: self.snooze(), font=("Arial", 24), bg='#4E4E4E', fg='white')
            snooze_button.pack(pady=20, fill='x', expand=True)
        else:
            # After all prompts, display the break screen
            self.show_break_screen(break_duration, todo_list, font_settings)

    def next_prompt(self, prompts, break_duration, todo_list, font_settings, index, answer_entry):
        # Here you can handle the answer, e.g., save it to a file or process it
        answer = answer_entry.get("1.0", tk.END).strip()
        print(f"Answer to prompt {index + 1}: {answer}")  # Example: print the answer

        # Move to the next prompt
        self.display_prompts(prompts, break_duration, todo_list, font_settings, index + 1)

    def show_break_screen(self, break_duration, todo_list, font_settings):
        # Clear any existing widgets
        for widget in self.workflow_frame.winfo_children():
            widget.destroy()

        # Display break time message
        quote = get_inspirational_quote()
        tk.Label(self.workflow_frame, text=quote, font=font_settings, bg='black', fg='white').pack(expand=True, pady=10)
        tk.Label(self.workflow_frame, text="To-do List:", font=font_settings, bg='black', fg='white').pack(expand=True, pady=10)
        
        for item in todo_list:
            tk.Label(self.workflow_frame, text=item, font=font_settings, bg='black', fg='white').pack(expand=True, pady=10)

        self.countdown(break_duration * 60, "Break")
        # Schedule to return to the settings screen after the break duration
        # Snooze button
        snooze_button = tk.Button(self.workflow_frame, text="Snooze", command=lambda: self.snooze(), font=("Arial", 24), bg='#4E4E4E', fg='white')
        snooze_button.pack(pady=20, fill='x', expand=True)

    def snooze(self):
        # Hide the current frame
        self.workflow_frame.pack_forget()
        self.run_session(self.snooze_duration, self.break_duration, self.todo_list, num_mindfulness_reminders=0, is_snooze=True)# Schedule to return to the current activity after the snooze duration
        
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
        if self.alarm_playing:
            self.alarm_playing = True
            threading.Thread(target=self.play_alarm).start()

    def on_focus_in(self, event):
        self.alarm_playing = False

    def play_alarm(self):
        while self.alarm_playing:
            playsound('gentle_alarm.mp3')

    def schedule_mindfulness_reminders(self, session_duration, num_reminders):
        print(f"Scheduling {num_reminders} mindfulness reminders over {session_duration} minutes")
        session_duration = session_duration - self.pre_break_warning_duration_minutes
        print(f"After adjusting for pre-break warning, we have {session_duration} minutes to divide among {num_reminders} reminders")
        if num_reminders == 0:
            return
        interval = session_duration / (num_reminders + 1)
        print(f"That equates to {interval} minutes between reminders")
        for i in range(1, num_reminders + 1):
            self.root.after(int(i * interval * 60 * 1000), self.play_mindfulness_bell_and_reminder)

    def play_mindfulness_bell_and_reminder(self, mindfulness_reminder=""):
        # if mindfulness reminder is empty, pick a random one
        if mindfulness_reminder == "":
            mindfulness_reminder = random.choice(self.mindfulness_reminders)
        sound = pygame.mixer.Sound('deep_bell.wav')
        clip_length = sound.get_length()
        # set volume to 50%
        sound.set_volume(0.5)
        sound.play()
        time.sleep(clip_length * .25)
        self.play_mindfulness_reminder(mindfulness_reminder)

    def play_mindfulness_reminder(self, reminder):
        subprocess.run(['espeak', '-s', '120', reminder])

    def create_list_item_widget(self, frame, items):
        font_settings = ("Arial", 36)  # 3 times bigger than typical size
        bg_color = '#2E2E2E'  # Dark background
        fg_color = '#FFFFFF'  # White text

        listbox = tk.Listbox(frame, font=font_settings, bg=bg_color, fg=fg_color, selectbackground='#4E4E4E', selectforeground=fg_color)
        listbox.pack(fill='both', expand=True)

        for item in items:
            listbox.insert(tk.END, item)

        entry = tk.Entry(frame, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        entry.pack()

        def add_item():
            item = entry.get()
            if item:
                listbox.insert(tk.END, item)
                entry.delete(0, tk.END)

        def remove_item():
            selected = listbox.curselection()
            if selected:
                listbox.delete(selected)

        add_button = tk.Button(frame, text="Add", command=add_item, font=font_settings, bg='#4E4E4E', fg=fg_color)
        add_button.pack()

        remove_button = tk.Button(frame, text="Remove", command=remove_item, font=font_settings, bg='#4E4E4E', fg=fg_color)
        remove_button.pack()

        return listbox

if __name__ == "__main__":
    root = tk.Tk()
    app = BreakApp(root)
    # Example usage of create_list_item_widget
    example_frame = tk.Frame(root)
    example_frame.pack(fill='both', expand=True)
    app.create_list_item_widget(example_frame, ["Project 1", "Project 2", "Project 3"])
    root.mainloop()