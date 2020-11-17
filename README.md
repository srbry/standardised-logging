# Standardised Logging

A python log handler to ship standardised logs.

## Installation

`pip install git+https://github.com/srbry/standardised-logging.git`

## Usage

```python
from standardised_logging import StandardisedLogger

logger = StandardisedLogger(
    name="my-logger",
    service="test-service",
    component="test-component",
    environment="dev",
    deployment="test-deployment",
)
```

### StandardisedLogger

Takes all the args of `StandardisedLogHandler` plus a `name` that is used for the same namespacing as the built-in
python logger, it will not appear in logs.

### StandardisedLogHandler

**Args**:

| Argument    | Type           | Default                                                                                                  |
|-------------|----------------|----------------------------------------------------------------------------------------------------------|
| service     | str            | N/A                                                                                                      |
| component   | str            | N/A                                                                                                      |
| environment | str            | N/A                                                                                                      |
| deployment  | str            | N/A                                                                                                      |
| user        | str            | `None` - When set to None the handler will detect the current logged in user                             |
| timezone    | str            | `UTC`                                                                                                    |
| context     | immutables.Map | `None` - Will auto generate a context in the form `{"log_correlation_id": uuid, "log_level": log_level}` |
| log_level   | int            | `logging.INFO` - This is only used if `context` is set to `None`                                         |
| stream      | IO             | `sys.stdout`                                                                                             |

### Context

A context should be an immutable Map with the properties `log_correlation_id` and `log_level`.

The intention of a context is that the initialising process will configure it and pass it down to any other
initialisations. As a result of this logs can be correlated using the `log_correlation_id` and the `log_level`
is auto set based on the top level initialisation. This works particularly well with serverless constructs where
your module and function is effectively the same thing.

Example:

```python
from standardised_logging import StandardisedLogger

logger = StandardisedLogger(
    service="test-service",
    component="test-component",
    environment="dev",
    deployment="test-deployment",
)

def handler(event, context):
    logger.info("Lambda started")
    return "I ran my lambda"
```

Result:
```json
{"log_level":"INFO","timestamp":"2020-11-17T12:14:58.990943+00:00","description":"Lambda started","user":"test-user","service":"test-service","component":"test-component","environment":"dev","deployment":"test-deployment","log_correlation_id":"e00b4eb1-a853-4955-b38a-fb4a5ea305e4","configured_log_level":"INFO"}
```

However this may not be the desired behaviour in long running app as your `context` is separate
from your apps lifecycle.

In this instance it is recommended that you pass your desired context to your calling application.

Example:

```python
def my_function(context, my_var):
    with logger.override_context(context):
        logger.info("Started my_function")
    return my_var
```
