import bcrypt
from db import execute, fetch_one


# -------------------------
# PASSWORD FUNCTIONS
# -------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode(),
            password_hash.encode()
        )
    except:
        return False


# -------------------------
# USER DATABASE FUNCTIONS
# -------------------------

def get_user_by_username(username):
    return fetch_one(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )


def create_user(org_id, username, password, full_name, email, role):
    password_hash = hash_password(password)

    execute("""
        INSERT INTO users
        (org_id, username, password_hash, full_name, email, role, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,NOW())
    """, (
        org_id,
        username,
        password_hash,
        full_name,
        email,
        role
    ))
