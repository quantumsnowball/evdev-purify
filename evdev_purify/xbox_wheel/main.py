import logging
from typing import Annotated

from typer import Argument, Option, Typer

from .purifier import Purifier

app = Typer()


logger = logging.getLogger(__file__)


@app.command(
    no_args_is_help=True,
    help='Xbox wheel event purifier',
)
def xbox_wheel(
    name: Annotated[str, Argument(help='The device name from evtest')],
    debug: Annotated[bool, Option(help='Enable debug mode verbose output')] = False,
) -> None:
    # logger
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(levelname)s [%(filename)s:%(lineno)d] %(message)s' if debug else '%(message)s',
    )

    # device
    purifier = Purifier(name)

    # run
    try:
        purifier.run()
    except KeyboardInterrupt:
        logger.info('\nPurifier Stopped by user.')
