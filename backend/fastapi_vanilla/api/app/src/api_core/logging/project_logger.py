import datetime as dt
import json
import logging
import logging.config
import atexit
import pathlib
from typing import override

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info", "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logging.

    This formatter is used to format log records as JSON objects.
    """

    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] | None = None
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exception"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        return json.dumps(message)


def setup_logging(config_path: str) -> None:
    """Setup the logging configuration.
    The config is loaded from a JSON file  
    Also starts the queue handler listener asynchronously so that logs are processed in the background.
    Parameters:
        config_path (str): The path to the logging configuration file.
    """
    try:
        with open(pathlib.Path(config_path), "r") as f:
            logging_config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Logging configuration file not found at: {config_path}")
    except json.JSONDecodeError:
        print(f"Failed to parse logging configuration file: {config_path}")
        raise

    try:
        logging.config.dictConfig(logging_config)
    except Exception as e:
        print(f"Error in logging configuration: {e}")
        raise

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is None:
        raise ValueError("queue_handler not found in logging configuration")
    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)
    logging.info("logging configured")
