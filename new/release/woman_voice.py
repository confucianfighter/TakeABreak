from gtts import gTTS
import pygame
import io

# Define the text
text = "Hello, I'm Steven Hawking, it's time to be productive."

# Create the gTTS object
tts = gTTS(text=text, lang='en', slow=False)

# Save to a bytes buffer instead of a file
audio_data = io.BytesIO()
tts.write_to_fp(audio_data)
audio_data.seek(0)

# Initialize pygame mixer and play audio
pygame.mixer.init()
pygame.mixer.music.load(audio_data, "mp3")
pygame.mixer.music.play()

# Keep the program running until the audio finishes
while pygame.mixer.music.get_busy():
    pass
