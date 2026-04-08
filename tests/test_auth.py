from unittest.mock import MagicMock, patch
from ms_planner.auth import get_token
from ms_planner.config import Settings


def _make_settings() -> Settings:
    return Settings(
        tenant_id="t-123",
        client_id="c-456",
        client_secret="s-789",
    )


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_from_cache(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = {"access_token": "cached-token"}
    mock_cca_cls.return_value = mock_app

    token = get_token(_make_settings())
    assert token == "cached-token"
    mock_app.acquire_token_silent.assert_called_once()
    mock_app.acquire_token_for_client.assert_not_called()


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_acquires_new(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {"access_token": "new-token"}
    mock_cca_cls.return_value = mock_app

    token = get_token(_make_settings())
    assert token == "new-token"


@patch("ms_planner.auth.msal.ConfidentialClientApplication")
def test_get_token_raises_on_error(mock_cca_cls):
    mock_app = MagicMock()
    mock_app.acquire_token_silent.return_value = None
    mock_app.acquire_token_for_client.return_value = {
        "error": "invalid_client",
        "error_description": "Bad credentials",
    }
    mock_cca_cls.return_value = mock_app

    import pytest
    with pytest.raises(RuntimeError, match="Bad credentials"):
        get_token(_make_settings())
