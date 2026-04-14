from typing import Annotated

from typer import Argument, Option, Typer

app = Typer()


@app.command(
    no_args_is_help=True,
    help='mouse-wheel event purifier',
)
def mouse_wheel(
    name: Annotated[str, Argument(help='The device name from evtest')],
) -> None:
    print('mouse-wheel sub-command')
    print(f'{name=}')
