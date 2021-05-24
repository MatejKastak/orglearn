import contextlib
import logging
import os
import pathlib
import sys
import typing


@contextlib.contextmanager
def Workdir(workdir: typing.Union[str, pathlib.Path]) -> typing.Iterator[None]:
    old_dir = os.getcwd()
    os.chdir(str(workdir))

    yield

    os.chdir(old_dir)


def setup_loggging(log_level: int) -> None:
    """Setup the default application logging."""

    # Configure the application logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Default logging is to stderr
    logging_handler = logging.StreamHandler(stream=sys.stderr)

    logging_handler.setFormatter(
        logging.Formatter(
            "[{asctime}] [{name:>15}:{lineno:<3}] [{levelname:.4}] -- {message}",
            style="{",
        )
    )

    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.addHandler(logging_handler)
