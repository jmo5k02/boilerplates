import logging

# from app.settings import LOG_LEVEL
from app.utils.enums import AppEnum

LOG_LEVEL = "DEBUG"

LOG_FORMAT_DEBUG = "%(levelname)s|%(message)s|%(pathname)s|%(funcName)s|%(lineno)d"


class LogLevels(AppEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging():
    log_level = str(LOG_LEVEL).upper()  # cast to string
    log_levels = list(LogLevels)

    if log_level not in log_levels:
        # we use error as the default log level
        logging.basicConfig(level=LogLevels.error)
        return

    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)
