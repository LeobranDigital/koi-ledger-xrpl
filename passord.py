import bcrypt

password = "demo123".encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())
