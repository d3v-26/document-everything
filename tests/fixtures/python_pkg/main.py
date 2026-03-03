"""Main entry point for python_pkg fixture."""
from .utils.helpers import format_name


def main():
    print(format_name("world"))


if __name__ == "__main__":
    main()
