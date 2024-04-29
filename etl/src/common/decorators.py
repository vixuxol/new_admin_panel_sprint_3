from functools import wraps
import logging
from time import sleep
from typing import Callable

logger = logging.getLogger(__name__)


def backoff(
    start_sleep_time: float = 1,
    factor: float = 2,
    border_sleep_time: float = 60,
) -> Callable:
    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as error:
                    logger.warning(f"An error arised: {error}. Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                    sleep_time = min(sleep_time * factor, border_sleep_time)

        return inner

    return func_wrapper
