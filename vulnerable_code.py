import os
import subprocess
import pickle

def run_command(user_input):
    """Run a shell command - SAFE version."""
    allowed = ["ls", "pwd", "whoami"]
    if user_input in allowed:
        return subprocess.run([user_input], capture_output=True)
    return None

def read_config():
    """Read configuration file."""
    with open("config.json", "r") as f:
        return f.read()

def get_username():
    """Get current username."""
    return os.getenv("USER", "unknown")

