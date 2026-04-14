from typer import Typer

app = Typer()


@app.command(
    no_args_is_help=True,
    help='keyboard event purifier',
)
def keyboard() -> None:
    print('keyboard sub-command')
