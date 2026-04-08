import pytest
from unittest.mock import AsyncMock
import ms_planner.auth as auth_module
from ms_planner.client import GraphClient


@pytest.fixture(autouse=True)
def clear_auth_cache():
    """Clear the MSAL app cache between tests to prevent state leakage."""
    auth_module._app_cache.clear()
    yield
    auth_module._app_cache.clear()


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=GraphClient)
    client.get_etag = lambda path: None
    client.set_etag = lambda path, etag: None
    return client
