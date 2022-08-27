"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Elastica Pipelines."""


if __name__ == "__main__":
    main(prog_name="elastica-pipelines")  # pragma: no cover
