import importlib.metadata as meta

from typer import Typer

NAME = 'evdev-purify'


app = Typer(
    name=NAME,
    no_args_is_help=True,
    help='A tool to purify the event flow for any evdev device',
)


@app.command(help='show version info')
def version() -> None:
    print(f'v{meta.version(NAME)}')
