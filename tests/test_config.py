import os
from ms_planner.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("TENANT_ID", "t-123")
    monkeypatch.setenv("CLIENT_ID", "c-456")
    monkeypatch.setenv("CLIENT_SECRET", "s-789")

    settings = Settings()
    assert settings.tenant_id == "t-123"
    assert settings.client_id == "c-456"
    assert settings.client_secret == "s-789"


def test_settings_missing_env_raises(monkeypatch):
    monkeypatch.delenv("TENANT_ID", raising=False)
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.delenv("CLIENT_SECRET", raising=False)

    import pytest
    with pytest.raises(Exception):
        Settings()
