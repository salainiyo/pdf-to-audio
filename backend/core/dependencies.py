from typing import Optional


def check_null_env(env_var: Optional[str]):
    """Raise ValueError if environment variable is None"""
    if not env_var:
        raise ValueError("Check environment variable")
    return env_var