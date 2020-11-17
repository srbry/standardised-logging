import logging
import sys
from pathlib import Path
from uuid import uuid4

import immutables

MAIN_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(MAIN_DIR))

from standardised_logging import StandardisedLogHandler  # noqa: E402

main_context = immutables.Map(log_correlation_id=str(uuid4()), log_level=logging.INFO)

secondary_context = immutables.Map(
    log_correlation_id=str(uuid4()), log_level=logging.DEBUG
)

log_handler = StandardisedLogHandler(
    service="test-service",
    component="test-component",
    environment="dev",
    deployment="test-deployment",
    user="test-user",
    context=main_context,
)
logger = logging.getLogger()
logger.addHandler(log_handler)
# This level is overridden by the handler
# setting it to debug gives the handler complete control
logger.setLevel(logging.DEBUG)

print(f"Starting logger with context: {main_context}\n")
logger.debug("This debug message should not be visible")
logger.info("Got to love an info message")
logger.warning("But be careful, there be dragons!")

with log_handler.override_context(secondary_context):
    logger.debug("In this context i can print debugs!")
