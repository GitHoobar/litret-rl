import ssl

# This will trigger SonarQube rule S4423
context = ssl.SSLContext(ssl.PROTOCOL_SSLv2)

print("hello from c.py")
colors = ["red", "green", "blue"]
print(f"Favorite color: {colors[1]}")
