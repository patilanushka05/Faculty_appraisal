import pytest
import asyncio
from unittest.mock import patch
import passlib.handlers.bcrypt
from src.setup.database import engine

# Fix passlib + bcrypt 4.0+ incompatibility
try:
    import bcrypt
    original_hashpw = bcrypt.hashpw
    def mocked_hashpw(password, salt):
        # Truncate to 72 bytes to avoid ValueError in bcrypt 4.0+
        if isinstance(password, str):
            password = password.encode('utf-8')
        if len(password) > 72:
            password = password[:72]
        return original_hashpw(password, salt)
    bcrypt.hashpw = mocked_hashpw
except (ImportError, AttributeError):
    pass

@pytest.fixture(scope="function", autouse=True)
async def cleanup_connections():
    yield
    # Dispose the engine pool to avoid "Event loop is closed" errors
    # when connections are returned to the pool after the loop is closed.
    await engine.dispose()

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
