import functools
import logging
import time
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

ToBeWrapped = Callable[P, R]
Wrapped = Callable[P, R]
Wrapper = Callable[[ToBeWrapped[P, R]], Wrapped[P, R]]


logger = logging.getLogger(__file__)


def retry_loop(
    *,
    welcome_message: str = '',
    oserror_message: str = '',
    init_delay: float = 0.0,
    retry_delay: float = 1.0,
) -> Wrapper:
    def wrapper(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:

        # wrapped function
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:

            # welcome
            logger.info(welcome_message)

            # init delay
            time.sleep(init_delay)

            # retry loop
            while True:
                try:
                    # actual logics
                    func(*args, **kwargs)

                except OSError:
                    logger.info(oserror_message)
                except Exception as e:
                    logger.error(e)

                # retry delay
                time.sleep(retry_delay)

            # This function is long running
            # It never returns

        # return the wrapped function
        return wrapped

    # return the wrapper
    return wrapper
