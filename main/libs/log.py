import json
import logging
import sys

from main import config


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(config.LOGGING_LEVEL)

    formatter = logging.Formatter(
        "[%(asctime)s][%(name)s][%(levelname)s]"
        " (%(module)s:%(funcName)s:%(lineno)d) %(message)s",
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    logger.propagate = False

    return logger


class _CustomLogger(logging.Logger):
    def _log(  # type: ignore[override]
        self,
        level: int,
        msg: str,
        args,
        data=None,
        **kwargs,
    ):
        if data:
            msg = f"{msg} | {json.dumps(data, default=str)}"

        # noinspection PyProtectedMember
        super()._log(level, msg, args, **kwargs)


logging.Logger.manager.loggerClass = _CustomLogger
