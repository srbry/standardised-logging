import logging
import sys
from contextlib import contextmanager
from typing import IO, Iterator, Union

import immutables

from standardised_logging import StandardisedLogHandler


class StandardisedLogger(logging.Logger):
    def __init__(
        self,
        name: str,
        service: str,
        component: str,
        environment: str,
        deployment: str,
        user: str = None,
        timezone: str = "UTC",
        context: immutables.Map = None,
        log_level: int = logging.INFO,
        stream: IO = sys.stdout,
    ) -> None:
        # We want the log level to be managed by the context on our Handler
        # Setting the loggers log level to debug ensures this works
        super().__init__(name, logging.DEBUG)
        self.standard_handler = StandardisedLogHandler(
            service=service,
            component=component,
            environment=environment,
            deployment=deployment,
            user=user,
            timezone=timezone,
            context=context,
            log_level=log_level,
            stream=stream,
        )
        self.handlers = [self.standard_handler]

    def setLevel(self, level: Union[int, str]) -> None:
        raise LogLevelException(
            "StandardisedLogger does not support setting log level this way. "
            + "Please set the log level using the 'log_level' attribute "
            + "on your context"
        )

    @contextmanager
    def override_context(self, context: immutables.Map) -> Iterator[None]:
        main_context = self.standard_handler._context
        main_level = self.standard_handler.level
        try:
            self.standard_handler._context = context
            self.standard_handler.level = context.get("log_level", logging.INFO)
            yield
        finally:
            self.standard_handler._context = main_context
            self.standard_handler.level = main_level


class LogLevelException(Exception):
    pass
