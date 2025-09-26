import ssl

# This will trigger SonarQube rule S4423
context = ssl.SSLContext(ssl.PROTOCOL_SSLv2)

print("hi")
