from typer import Typer

app = Typer()


@app.command(
    no_args_is_help=True,
    help='mouse-wheel event purifier',
)
def mouse_wheel() -> None:
    print('mouse-wheel sub-command')
