"""Build command."""
import click


@click.command()
@click.option("--output", default="dist", help="Output directory")
def build(output):
    """Build the project."""
    click.echo(f"Building to {output}...")
