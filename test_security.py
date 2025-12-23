import sqlite3

def get_user_by_id(user_id):
    """Get user from database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchone()

def get_user_by_name(name):
    """Get user by name - safe version."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cursor.fetchone()


API_KEY = "sk-1234567890abcdef1234567890abcdef"

def call_api():
    return {"key": API_KEY}
