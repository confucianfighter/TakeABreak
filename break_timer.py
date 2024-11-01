import pygame
import time
import requests
import sys
import ctypes
import json
import random
import win32gui
from settings_manager import settings  # Assuming settings.py is in the same directory
import win32event
import win32api
import winerror
import toml

# Your main app code here

# Initialize pygame mixer
pygame.mixer.init()

# Load the alarm sound
alarm_sound = pygame.mixer.Sound('gentle_alarm.mp3')

# Constants for setting the window to stay on top
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_SHOWWINDOW = 0x0040

# Function to set the window to stay on top
def set_window_topmost():
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

# Function to get an inspirational quote
def get_inspirational_quote():
    print("Getting inspirational quote from zenquotes.io")
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        quote_data = response.json()[0]
        return f'"{quote_data["q"]}"\n- {quote_data["a"]}'
    else:
        return "Keep going, you're doing great!"

# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    width, _ = font.size(' ')

    for word in words:
        word_width, _ = font.size(word)
        if width + word_width <= max_width:
            current_line.append(word)
            width += word_width + font.size(' ')[0]
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            width = word_width + font.size(' ')[0]

    lines.append(' '.join(current_line))
    return lines

def initialize_pygame():
    initialized = False
    for _ in range(3):
        try:
            pygame.init()
            info = pygame.display.Info()
            screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            initialized = True
            break
        except pygame.error:
            time.sleep(1)

    if not initialized:
        print("Failed to initialize pygame")
        sys.exit(1)

    return info, screen


def display_input_prompt(prompt, small_font):
    global running
    input_active = True
    user_input = ''
    while input_active and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

        # Check if the window is in focus
        foreground_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if "Break Time" in foreground_window:
            on_focus_in()
        else:
            on_focus_out()

        screen.fill(black)
        prompt_text = small_font.render(prompt, True, white)
        input_text = small_font.render(user_input, True, white)
        screen.blit(prompt_text, (info.current_w / 2 - prompt_text.get_width() / 2, info.current_h / 2 - 50))
        screen.blit(input_text, (info.current_w / 2 - input_text.get_width() / 2, info.current_h / 2))
        pygame.display.update()
    return user_input

# Function to handle focus loss
def on_focus_out():
    global alarm_playing
    if not alarm_playing:
        print("Break window lost focus, please bring it to the front.")
        alarm_sound.play(loops=-1)
        alarm_playing = True

# Function to handle focus gain
def on_focus_in():
    global alarm_playing
    if alarm_playing:
        alarm_sound.stop()
        alarm_playing = False

# Function to display the break screen
def display_break_screen(elapsed_time, break_time, quote, todo_list, small_font, font):
    screen.fill(black)
    wrapped_quote = wrap_text(quote, small_font, info.current_w - 100)
    y_offset = info.current_h / 2 - (len(wrapped_quote) / 2) * 60

    for line in wrapped_quote:
        text = small_font.render(line, True, white)
        text_rect = text.get_rect(center=(info.current_w / 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 60

    # Display countdown timer
    remaining_time = break_time - elapsed_time
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    # convert seconds to integer
    seconds = int(seconds)
    countdown_text = font.render(f'Time remaining: {minutes:02}:{seconds:02}', True, white)
    countdown_rect = countdown_text.get_rect(center=(info.current_w / 2, info.current_h - 100))
    screen.blit(countdown_text, countdown_rect)
    random_entry = ""
    # Display to-do list
    y_offset = info.current_h / 2 + 100
    item="For this break you had set the intention to:"
    text = small_font.render(item, True, white)
    text_rect = text.get_rect(center=(info.current_w / 2, y_offset))
    screen.blit(text, text_rect)
    y_offset += 60
    for item in todo_list:
        text = small_font.render(item, True, white)
        text_rect = text.get_rect(center=(info.current_w / 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 60

    pygame.display.update()

# Load writing prompts from the TOML file
def load_writing_prompts():
    with open('writing_prompts.toml', 'r') as file:
        data = toml.load(file)
    return data['prompts']

try:
    info, screen = initialize_pygame()
    pygame.display.set_caption('Break Time')

    # Ensure the window stays on top
    set_window_topmost()

    # Define colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Load font
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Get break duration and to-do list from command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python break_timer.py <break_duration_in_seconds> <todo_list>")
        sys.exit(1)

    break_duration = float(sys.argv[1])
    todo_list = json.loads(sys.argv[2])

    # Get an inspirational quote
    quote="Couldn't get online to retrive an inspirational quote."
    try:
        quote = get_inspirational_quote()
    except:
        pass

    # Alarm control
    alarm_playing = False
    running = True

    # Load or initialize settings
    combined_list = settings.get('combined_list', [])

    # Load writing prompts
    writing_prompts = load_writing_prompts()

    # Prompt user for inputs if the list is empty
    questions = [
        "Enter a positive affirmation:",
        "Enter a statement of acceptance:",
        "Enter a statement of gratitude:"
    ]

    # Randomly choose one question to replace with a writing prompt
    question_to_replace = random.choice(questions)
    random_prompt = random.choice(writing_prompts)

    # Replace the chosen question with the random writing prompt
    questions[questions.index(question_to_replace)] = random_prompt

    # Collect user inputs
    user_inputs = []
    for question in questions:
        user_input = display_input_prompt(question, small_font)
        user_inputs.append(user_input)

    combined_list.extend(user_inputs)
    settings.set('combined_list', combined_list)

    random_entry = random.choice(combined_list)

    # Main loop for break timer after prompts
    start_time = time.time()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check if the window is in focus
        foreground_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if "Break Time" in foreground_window:
            on_focus_in()
        else:
            on_focus_out()

        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time >= break_duration:
            running = False
        else:
            display_break_screen(elapsed_time, break_duration, quote, todo_list + [random_entry], small_font, font)
            time.sleep(1)

        # Ensure the window stays on top
        set_window_topmost()

except pygame.error as e:
    print(f"Pygame error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
