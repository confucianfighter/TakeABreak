import subprocess

text = "Hello, I'm Stephen Hawking. It's time to be productive."
subprocess.run(["espeak", "-s120", text])  # -s140 sets the speed; adjust as needed
