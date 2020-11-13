import getpass
import json
import logging

from freezegun import freeze_time


def parse_log_lines(logs):
    log_lines = []
    split_logs = logs.split("\n{")
    for line in split_logs:
        if line.startswith('"'):
            line = "{" + line
        log_lines.append(json.loads(line))
    return log_lines


@freeze_time("2020-11-13")
def test_logging(logger, log_stream, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("my info log message")
        logger.debug("my debug log message")
        logger.warn("this is a warning")
        log_messages = parse_log_lines(log_stream.getvalue())
        assert len(log_messages) == 2
        assert len(log_messages[0]) == 8
        assert log_messages[0]["log_level"] == "INFO"
        assert log_messages[0]["timestamp"] == "2020-11-13T00:00:00+00:00"
        assert log_messages[0]["description"] == "my info log message"
        assert log_messages[0]["service"] == "test-service"
        assert log_messages[0]["component"] == "test-component"
        assert log_messages[0]["environment"] == "dev"
        assert log_messages[0]["deployment"] == "test-deployment"
        assert log_messages[0]["user"] == "test-user"
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
