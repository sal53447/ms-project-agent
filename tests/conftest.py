import pytest
import ms_planner.auth as auth_module


@pytest.fixture(autouse=True)
def clear_auth_cache():
    """Clear the MSAL app cache between tests to prevent state leakage."""
    auth_module._app_cache.clear()
    yield
    auth_module._app_cache.clear()
