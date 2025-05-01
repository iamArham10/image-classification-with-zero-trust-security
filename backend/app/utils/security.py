from passlib.context import CryptContext
import secrets
from fastapi import Request
from user_agents import parse
import re

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def is_strong_password(password: str) -> bool:
    return (
        len(password) >=8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    password_with_salt = password + salt
    hashed_password = pwd_context.hash(password_with_salt)
    return hashed_password, salt

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    pass_with_salt = plain_password + salt
    return pwd_context.verify(pass_with_salt, hashed_password)

def get_client_ip(request: Request) -> str:
    # x_forwarded is used if behind a proxy/load balancer
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host # direct client IP
    return ip

def get_device_info(request: Request) -> dict:
    user_agent_str = request.headers.get("User-Agent", "unknown")
    user_agent = parse(user_agent_str)

    return {
        "os": user_agent.os.family,
        "browser": user_agent.browser.family,
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_pc": user_agent.is_pc,
        "user_agent": user_agent_str
    }