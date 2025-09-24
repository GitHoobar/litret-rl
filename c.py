def read_file(filename):
    # Path traversal vulnerability
    with open(f"/var/www/{filename}", 'r') as f:
        return f.read()

print("hi")
