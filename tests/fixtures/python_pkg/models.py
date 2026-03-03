"""Data models for python_pkg."""
from .utils.helpers import format_name


class User:
    def __init__(self, name: str):
        self.name = format_name(name)
