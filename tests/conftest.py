import logging
from io import StringIO

import pytest

from standardised_logging import StandardisedLogger, StandardisedLogHandler


@pytest.fixture
def log_stream():
    return StringIO()


@pytest.fixture
def default_handler_config():
    return {
        "service": "test-service",
        "component": "test-component",
        "environment": "dev",
        "deployment": "test-deployment",
        "user": "test-user",
    }


@pytest.fixture
def log_handler(log_stream, default_handler_config):
    return StandardisedLogHandler(
        **default_handler_config,
        stream=log_stream,
    )


@pytest.fixture
def default_logger(default_handler_config, log_stream):
    return StandardisedLogger(
        name="default_standardised_logger", **default_handler_config, stream=log_stream
    )


@pytest.fixture
def logger(log_handler):
    logs = logging.getLogger("test")
    logs.addHandler(log_handler)
    return logs


@pytest.fixture
def log_record():
    record = logging.LogRecord(
        name="test",
        level="INFO",
        pathname="pathname",
        lineno=1,
        msg="test",
        args=None,
        exc_info=None,
    )
    record.created = 1605225600
    return record
