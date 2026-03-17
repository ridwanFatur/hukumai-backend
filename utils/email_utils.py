import re


def extract_name_from_email(email: str) -> str:
    local_part = email.split("@")[0]
    parts = re.split(r'[^a-zA-Z]+', local_part)
    parts = [p for p in parts if p][:2]
    name = " ".join(p.capitalize() for p in parts)
    return name


def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
