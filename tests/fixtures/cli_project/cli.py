"""CLI entry point."""
import click
from commands.build import build


@click.group()
def cli():
    """Test CLI tool."""
    pass


cli.add_command(build)

if __name__ == "__main__":
    cli()
