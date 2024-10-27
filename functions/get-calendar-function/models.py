from dataclasses import dataclass


@dataclass
class User:
    login: str
    password: str
    key_id: str
    version_id: str
