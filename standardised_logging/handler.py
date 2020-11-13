import json
import sys
from datetime import datetime
from getpass import getuser
from logging import INFO, LogRecord, StreamHandler, getLevelName
from typing import IO
from uuid import uuid4

import immutables
import pytz


class StandardisedLogHandler(StreamHandler):
    def __init__(
        self,
        service: str,
        component: str,
        environment: str,
        deployment: str,
        user: str = None,
        timezone: str = "UTC",
        context: immutables.Map = None,
        log_level: int = INFO,
        stream: IO = sys.stdout,
    ) -> None:
        self.service = service
        self.component = component
        self.environment = environment
        self.deployment = deployment
        self.user = user
        self.timezone = timezone
        super().__init__(stream=stream)

        if context is None:
            context = immutables.Map(
                log_correlation_id=str(uuid4()), configured_log_level=log_level
            )
        self._context = context
        self.level = self._context.get("configured_log_level", INFO)

    def emit(self, record: LogRecord) -> None:
        self.level = self._context.get("configured_log_level", INFO)
        super().emit(record)

    def format(self, record: LogRecord) -> str:
        log_message = {
            "log_level": record.levelname,
            "timestamp": self.get_timestamp(record),
            "description": record.getMessage(),
            "user": self.get_user(),
            "service": self.service,
            "component": self.component,
            "environment": self.environment,
            "deployment": self.deployment,
        }
        log_message = {
            **log_message,
            **self._context,
            "configured_log_level": getLevelName(self.level),
        }
        return json.dumps(log_message, separators=(",", ":"))

    def get_user(self) -> str:
        if self.user is not None:
            return self.user
        return getuser()

    def get_timestamp(self, record: LogRecord) -> str:
        tz = pytz.timezone(self.timezone)
        return datetime.fromtimestamp(record.created, tz).isoformat()

    def set_context_attribute(self, attribute_name: str, attribute_value: str) -> None:
        if attribute_name in self._context:
            raise ImmutableContextError(attribute_name)
        self._context = self._context.set(attribute_name, attribute_value)


class ImmutableContextError(Exception):
    def __init__(self, attribute_name: str) -> None:
        self.attribute_name = attribute_name
        super().__init__()

    def __str__(self) -> str:
        return (
            "Context attributes are immutable, could not override "
            + f"'{self.attribute_name}'"
        )
