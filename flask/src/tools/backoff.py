import logging
import time
from functools import wraps


def backoff(
    logger: logging.Logger = logging.getLogger(__name__),
    max_attempt_count: int = 5,
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: float = 10,
):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост
    времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error: {e}")

                    if attempt >= max_attempt_count:
                        raise e

                    attempt += 1
                    sleep_time = start_sleep_time * pow(factor, n + 1)
                    if sleep_time < border_sleep_time:
                        n += 1
                    else:
                        sleep_time = border_sleep_time

                    time.sleep(sleep_time)

        return inner

    return func_wrapper
