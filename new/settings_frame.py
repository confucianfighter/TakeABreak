def create_settings_frame(self):
        self.pack(fill='both', expand=True)

        # Load existing settings
        
        # Define font and color settings for the dark theme
        font_settings = ("Arial", 36)  # 3 times bigger than typical size
        bg_color = '#2E2E2E'  # Dark background
        fg_color = '#FFFFFF'  # White text

        self.configure(bg=bg_color)

        tk.Label(self, text="Enter session duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.session_entry = tk.Entry(self, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.session_entry.insert(0, str(self.session_duration))  # Convert seconds back to minutes
        self.session_entry.pack()

        tk.Label(self, text="Enter break duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.break_entry = tk.Entry(self, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.break_entry.insert(0, str(self.break_duration))  # Convert seconds back to minutes
        self.break_entry.pack()

        tk.Label(self, text="Enter to-do list (one item per line):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.todo_text = tk.Text(self, height=5, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.todo_text.insert("1.0", "\n".join(self.todo_list))
        self.todo_text.pack()

        tk.Label(self, text="Enter number of mindfulness reminders:", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.reminders_entry = tk.Entry(self, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
        self.reminders_entry.insert(0, str(self.num_mindfulness_reminders))
        self.reminders_entry.pack()

        tk.Label(self, text="Enter pre-break warning duration (minutes):", font=font_settings, bg=bg_color, fg=fg_color).pack()
        self.pre_break_warning_entry = tk.Entry(self, font=font_settings, bg='#3E3E3E', fg=fg_color, insertbackground=fg_color)
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
        self.pack_forget()
        self.run_session(self.session_duration, self.break_duration, self.todo_list, self.num_mindfulness_reminders)
    