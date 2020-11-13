import json
import sys
from datetime import datetime
from getpass import getuser
from logging import LogRecord, StreamHandler
from typing import IO

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
        stream: IO = sys.stdout,
    ) -> None:
        self.service = service
        self.component = component
        self.environment = environment
        self.deployment = deployment
        self.user = user
        self.timezone = timezone
        super().__init__(stream=stream)

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
        return json.dumps(log_message, separators=(",", ":"))

    def get_user(self) -> str:
        if self.user is not None:
            return self.user
        return getuser()

    def get_timestamp(self, record: LogRecord) -> str:
        tz = pytz.timezone(self.timezone)
        return datetime.fromtimestamp(record.created, tz).isoformat()
