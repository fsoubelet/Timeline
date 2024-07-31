from pathlib import Path

import click

from loguru import logger

from pytimeline.structures import Timeline
from pytimeline.utils import config_logger


@click.command()
@click.option(
    "--inputfile",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, path_type=Path),
    required=True,
    help="Path to the input JSON file with the timeline data.",
)
@click.option(
    "--outputfile",
    type=click.Path(file_okay=True, resolve_path=True, path_type=Path),
    default=Path("timeline.svg"),
    help="Path at which to write the output SVG file.",
    show_default=True,
)
@click.option(
    "--logging",
    type=click.Choice(["trace", "debug", "info", "warning", "error", "critical"]),
    default="info",
    show_default=True,
    help="Sets the logging level.",
)
def main(inputfile: Path, outputfile: Path, logging: str):
    config_logger(logging)
    timeline = Timeline(filename=inputfile)
    timeline.build()
    timeline.save(filename=outputfile)


if __name__ == "__main__":
    main()
