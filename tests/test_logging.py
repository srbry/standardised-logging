import getpass
import json
import logging
from uuid import UUID, uuid4

import immutables
import pytest
from freezegun import freeze_time

from standardised_logging import (
    ImmutableContextError,
    LogLevelException,
    StandardisedLogger,
    StandardisedLogHandler,
)


def parse_log_lines(logs):
    log_lines = []
    split_logs = logs.split("\n{")
    for line in split_logs:
        if line.startswith('"'):
            line = "{" + line
        log_lines.append(json.loads(line))
    return log_lines


def is_valid_uuid(uuid_to_test):
    try:
        uuid = UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return str(uuid) == uuid_to_test


@freeze_time("2020-11-13")
def test_logging(logger, log_stream, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("my info log message")
        logger.debug("my debug log message")
        logger.warning("this is a warning")
        log_messages = parse_log_lines(log_stream.getvalue())
        assert len(log_messages) == 2
        assert len(log_messages[0]) == 10
        assert log_messages[0]["log_level"] == "INFO"
        assert log_messages[0]["timestamp"] == "2020-11-13T00:00:00+00:00"
        assert log_messages[0]["description"] == "my info log message"
        assert log_messages[0]["service"] == "test-service"
        assert log_messages[0]["component"] == "test-component"
        assert log_messages[0]["environment"] == "dev"
        assert log_messages[0]["deployment"] == "test-deployment"
        assert log_messages[0]["user"] == "test-user"
        assert log_messages[0]["configured_log_level"] == "INFO"
        assert is_valid_uuid(log_messages[0]["log_correlation_id"])
        assert log_messages[1]["log_level"] == "WARNING"
        assert log_messages[1]["description"] == "this is a warning"


def test_multiline_logging(logger, log_stream, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("my info log message\nwith an extra line")
        logger.info("a second log message")
        log_messages = parse_log_lines(log_stream.getvalue())
        assert (
            log_messages[0]["description"] == "my info log message\nwith an extra line"
        )
        assert log_messages[1]["description"] == "a second log message"


def test_get_user(log_handler):
    assert log_handler.get_user() == "test-user"


def test_get_user_dynamic(log_handler):
    log_handler.user = None
    assert log_handler.get_user() == getpass.getuser()


def test_get_timestamp(log_handler, log_record):
    assert log_handler.get_timestamp(log_record) == "2020-11-13T00:00:00+00:00"


def test_log_level_set_by_context(default_handler_config, log_stream):
    log_handler = StandardisedLogHandler(
        **default_handler_config,
        context=immutables.Map(
            log_correlation_id=str(uuid4()), log_level=logging.ERROR
        ),
        stream=log_stream,
    )
    logger = logging.getLogger("test_log_level_set_by_context")
    logger.addHandler(log_handler)
    logger.info("my info log message")
    logger.debug("my debug log message")
    logger.warning("this is a warning")
    logger.critical("this is a critical warning")
    logger.error("this is an error")
    log_messages = parse_log_lines(log_stream.getvalue())
    assert len(log_messages) == 2
    assert log_messages[0]["log_level"] == "CRITICAL"
    assert log_messages[0]["configured_log_level"] == "ERROR"
    assert log_messages[1]["log_level"] == "ERROR"
    assert log_messages[1]["configured_log_level"] == "ERROR"


def test_log_level_is_immutable(default_handler_config, log_stream):
    log_handler = StandardisedLogHandler(
        **default_handler_config,
        context=immutables.Map(log_correlation_id=str(uuid4()), log_level=logging.WARN),
        stream=log_stream,
    )
    logger = logging.getLogger("test_log_level_is_immutable")
    logger.addHandler(log_handler)
    log_handler.setLevel(logging.INFO)
    logger.warning("this is a warning")
    logger.info("my info log message")
    logger.debug("my debug log message")
    logger.critical("this is a critical warning")
    log_messages = parse_log_lines(log_stream.getvalue())
    assert len(log_messages) == 2
    assert log_messages[0]["log_level"] == "WARNING"
    assert log_messages[0]["configured_log_level"] == "WARNING"
    assert log_messages[0]["description"] == "this is a warning"
    assert log_messages[1]["log_level"] == "CRITICAL"
    assert log_messages[1]["configured_log_level"] == "WARNING"
    assert log_messages[1]["description"] == "this is a critical warning"


def test_set_context_attribute(caplog, logger, log_handler, log_stream):
    with caplog.at_level(logging.INFO):
        log_handler.set_context_attribute("my_attribute", "my_attribute_value")
        assert log_handler._context.get("my_attribute") == "my_attribute_value"
        logger.info("my info log message")
        log_messages = parse_log_lines(log_stream.getvalue())
        assert len(log_messages[0]) == 11
        assert log_messages[0]["my_attribute"] == "my_attribute_value"


def test_set_context_attribute_update(log_handler):
    with pytest.raises(ImmutableContextError) as err:
        log_handler.set_context_attribute("log_level", logging.DEBUG)
    assert (
        str(err.value)
        == "Context attributes are immutable, could not override 'log_level'"
    )


def test_override_context(default_handler_config, log_stream):
    log_handler = StandardisedLogHandler(
        **default_handler_config,
        context=immutables.Map(log_correlation_id="foobar", log_level=logging.INFO),
        stream=log_stream,
    )
    logger = logging.getLogger("test_override_context")
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    logger.info("my info log message")
    logger.debug("a debug message")
    with log_handler.override_context(
        immutables.Map(
            log_correlation_id="override_correlation_id",
            log_level=logging.DEBUG,
        )
    ):
        logger.debug("my overridden debug")
    log_messages = parse_log_lines(log_stream.getvalue())
    assert len(log_messages) == 2
    assert log_messages[0]["log_correlation_id"] == "foobar"
    assert log_messages[0]["description"] == "my info log message"
    assert log_messages[1]["log_correlation_id"] == "override_correlation_id"
    assert log_messages[1]["description"] == "my overridden debug"


def test_logger(default_handler_config, log_stream):
    logger = StandardisedLogger(
        name="test_logger",
        **default_handler_config,
        context=immutables.Map(log_correlation_id="foobar", log_level=logging.INFO),
        stream=log_stream,
    )
    logger.info("my info log message")
    logger.debug("a debug message")
    with logger.override_context(
        immutables.Map(
            log_correlation_id="override_correlation_id",
            log_level=logging.DEBUG,
        )
    ):
        logger.debug("my overridden debug")
    log_messages = parse_log_lines(log_stream.getvalue())
    assert len(log_messages) == 2
    assert log_messages[0]["log_correlation_id"] == "foobar"
    assert log_messages[0]["description"] == "my info log message"
    assert log_messages[1]["log_correlation_id"] == "override_correlation_id"
    assert log_messages[1]["description"] == "my overridden debug"


def test_setLevel(default_logger):
    with pytest.raises(LogLevelException) as err:
        default_logger.setLevel(logging.WARNING)
    assert str(err.value) == (
        "StandardisedLogger does not support setting log level this way. "
        + "Please set the log level using the 'log_level' attribute "
        + "on your context"
    )
