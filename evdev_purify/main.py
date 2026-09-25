import importlib.metadata as meta

from typer import Typer

from .ffb_wheel import app as ffb_wheel
from .ffb_wheel_companion import app as ffb_wheel_companion
from .keyboard import app as keyboard
from .mouse_wheel import app as mouse_wheel
from .xbox_wheel import app as xbox_wheel

NAME = 'evdev-purify'


app = Typer(
    name=NAME,
    no_args_is_help=True,
    help='A tool to purify the event flow for any evdev device',
)


@app.command(help='show version info')
def version() -> None:
    print(f'v{meta.version(NAME)}')


app.add_typer(keyboard)
app.add_typer(mouse_wheel)
app.add_typer(ffb_wheel)
app.add_typer(ffb_wheel_companion)
app.add_typer(xbox_wheel)
