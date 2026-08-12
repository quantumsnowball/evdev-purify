import logging
from typing import Annotated

from typer import Argument, Option, Typer

from .purifier import Purifier

app = Typer()

logger = logging.getLogger(__file__)


@app.command(
    no_args_is_help=True,
    help='ffb-wheel event purifier, output to companion keyboard',
)
def ffb_wheel_companion(
    name: Annotated[str, Argument(help='The device name from evtest')],
    layer_activation: Annotated[float, Option(help='Minimum hand pedal percentage to active the layer')] = 0.1,
    layer_hit: Annotated[int, Option(help='Minimum number of valid events required to activate a layer')] = 5,
    log_threshold: Annotated[int, Option(help='Package size threshold for logging large packages')] = 5,
    debug: Annotated[bool, Option(help='Enable debug mode verbose output')] = False,
) -> None:
    # logger
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(levelname)s [%(filename)s:%(lineno)d] %(message)s' if debug else '%(message)s',
    )

    # device
    purifier = Purifier(
        name,
        layer_activation=layer_activation,
        layer_hit=layer_hit,
        log_threshold=log_threshold,
    )

    # run
    try:
        purifier.run()
    except KeyboardInterrupt:
        logger.info('\nPurifier Stopped by user.')
