import os
import subprocess
import pickle

def run_command(user_input):
    """Execute command based on user input - VULNERABLE!"""
    # Command injection vulnerability (line 8) - NOT IN DIFF
    result = subprocess.call(user_input, shell=True)
    return result

def read_file(filename):
    """Read any file - VULNERABLE to path traversal!"""
    # Path traversal vulnerability (line 14) - NOT IN DIFF  
    with open(filename, "r") as f:
        return f.read()

def load_data(user_data):
    """Load serialized data - VULNERABLE!"""
    # Pickle deserialization vulnerability (line 20) - NOT IN DIFF
    return pickle.loads(user_data)

def get_username():
    """Get current username."""
    return os.getenv("USER", "unknown")


# NEW FUNCTION ADDED - This is what the PR changes (IN DIFF)
def get_all_env_vars():
    """Get all environment variables."""
    return dict(os.environ)

def format_output(data):
    """Format data as string."""
    return str(data)
