# Patisson Request

`Patisson Request` is a Python library designed for communication between microservices. It simplifies the process of sending HTTP requests, managing JWT tokens, and ensuring smooth interaction with external services using Pydantic models for request and response handling.

## Installation

You can install the library via `pip`:

```bash
pip install git+https://github.com/Patisson-Company/_Request
```

## Getting Started

To begin using `Patisson Request`, you need to initialize the `SelfAsyncService` class with the necessary configuration, such as the service name, login, password, and external services.

### Example Initialization

```python
from patisson_request.core import SelfAsyncService
from patisson_request.services import Service
import os

SelfService = SelfAsyncService( 
    self_service=Service("SERVICE_NAME"),
    login=os.getenv("LOGIN"),  # type: ignore[reportArgumentType]
    password=os.getenv("PASSWORD"),  # type: ignore[reportArgumentType]
    external_services=EXTERNAL_SERVICES,
    logger_object=logger
)
```

Here, `SelfAsyncService` is initialized with the following parameters:

- `self_service`: The name of your service.
- `login`: Login credentials for authentication.
- `password`: Password for authentication.
- `external_services`: A dictionary of external services to communicate with.
- `logger_object`: A logger instance for logging purposes.

## Sending Requests

The library simplifies sending HTTP requests to other services. You can use methods such as `post_request` and `get_request` to interact with remote APIs.

### Example Request

```python
response = await self.post_request(
    *-AuthenticationRoute.api.v1.service.jwt.create(
        login=self.login, password=self.password
    ), use_auth_token=False
)
```

