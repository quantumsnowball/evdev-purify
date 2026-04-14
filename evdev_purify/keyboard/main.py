import logging
from typing import Annotated

from typer import Argument, Option, Typer

from .purifier import Purifier

app = Typer()


logger = logging.getLogger(__file__)


@app.command(
    no_args_is_help=True,
    help='keyboard event purifier',
)
def keyboard(
    name: Annotated[str, Argument(help='The device name from evtest')],
    max_event_interval: Annotated[float, Option(help='Time interval (seconds) of events to be dropped (temporal debounce)')] = 0.05,
    debug: Annotated[bool, Option(help='Enable debug mode verbose output')] = False,
) -> None:
    # logger
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(levelname)s: %(message)s')

    # device
    purifier = Purifier(name, max_event_interval=max_event_interval)

    # run
    try:
        purifier.run()
    except KeyboardInterrupt:
        logger.info('\nPurifier Stopped by user.')
