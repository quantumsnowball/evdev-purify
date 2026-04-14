import logging
from typing import Annotated

from typer import Argument, Option, Typer

from .purifier import Purifier

app = Typer()

logger = logging.getLogger(__file__)


@app.command(
    no_args_is_help=True,
    help='mouse-wheel event purifier',
)
def mouse_wheel(
    name: Annotated[str, Argument(help='The device name from evtest')],
    delay: Annotated[float, Option(help='Delay (seconds) before re-firing events')] = 0.075,
    min_history_len: Annotated[int, Option(help='Minimum event count required in history to compute majority vote')] = 2,
    max_event_interval: Annotated[float, Option(help='Time interval (seconds) of events to be dropped (temporal debounce)')] = 0.01,
    debug: Annotated[bool, Option(help='Enable debug mode verbose output')] = False,
) -> None:
    # logger
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(levelname)s: %(message)s')

    # device
    purifier = Purifier(
        name,
        delay=delay,
        min_history_len=min_history_len,
        max_event_interval=max_event_interval
    )

    # run
    try:
        purifier.run()
    except KeyboardInterrupt:
        logger.info('\nPurifier Stopped by user.')
