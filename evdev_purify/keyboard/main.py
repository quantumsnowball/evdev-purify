from typing import Annotated

from typer import Argument, Option, Typer

app = Typer()


@app.command(
    no_args_is_help=True,
    help='keyboard event purifier',
)
def keyboard(
    name: Annotated[str, Argument(help='The device name from evtest')],
) -> None:
    print('keyboard sub-command')
    print(f'{name=}')
