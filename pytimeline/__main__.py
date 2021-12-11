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
    "--outputdir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
    help="Path to the directory in which to write the output SVG file. If not provided, will pick"
    "the directory of the input file.",
)
@click.option(
    "--logging",
    type=click.Choice(["trace", "debug", "info", "warning", "error", "critical"]),
    default="info",
    show_default=True,
    help="Sets the logging level.",
)
def main(inputfile: Path, outputdir: Path, logging: str):
    config_logger(logging)

    if not outputdir:
        logger.debug("No output directory provided, using input file directory.")
        outputdir = inputfile.parent
    outputfile = outputdir / "timeline.svg"

    timeline = Timeline(filename=inputfile)
    timeline.build()
    timeline.save(filename=outputfile)


if __name__ == "__main__":
    main()
