from fastapi import Request
from user_agents import parse
import re
import bcrypt

def is_strong_password(password: str) -> bool:
    return (
        len(password) >=8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Generate a hashed password with a salt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host # direct client IP
    return ip if ip else "unknown"

def get_device_info(request: Request) -> dict:
    user_agent_str = request.headers.get("User-Agent", "unknown")
    user_agent = parse(user_agent_str)

    return {
        "os": user_agent.os.family if user_agent.os else "unknown",
        "browser": user_agent.browser.family if user_agent.browser else "unknown",
        "device": user_agent.device.family if user_agent.device else "unknown",
        "user_agent": user_agent_str if user_agent_str else "unknown"
    }