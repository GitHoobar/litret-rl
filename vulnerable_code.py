import ssl
import hashlib
import subprocess

# Line 5: Normal code
def safe_function():
    return "Hello"

# Line 9-10: SSL vulnerability (SonarQube S4423)
def create_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv2)
    return context

# Line 14-15: Weak hash vulnerability (SonarQube S4790)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Line 19-20: Command injection (SonarQube S2076)  
def run_command(user_input):
    subprocess.call(user_input, shell=True)

# Line 23: Hardcoded secret
API_KEY = "sk-secret123456789"
