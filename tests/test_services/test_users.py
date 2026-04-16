import pytest
from ms_planner.services.users import UserService
from ms_planner.models import User


@pytest.fixture
def service(mock_client):
    return UserService(mock_client)


@pytest.mark.asyncio
async def test_get_by_id(service, mock_client):
    mock_client.get.return_value = {
        "id": "abc-123",
        "displayName": "Pouyan Salehi",
        "mail": "pouyan.salehi@stock-solution.de",
        "userPrincipalName": "pouyan.salehi@stock-solution.de",
    }
    user = await service.get("abc-123")
    assert user.id == "abc-123"
    assert user.display_name == "Pouyan Salehi"
    mock_client.get.assert_called_once_with("/users/abc-123")


@pytest.mark.asyncio
async def test_get_by_email(service, mock_client):
    mock_client.get.return_value = {
        "id": "abc-123",
        "displayName": "Pouyan Salehi",
        "mail": "pouyan.salehi@stock-solution.de",
        "userPrincipalName": "pouyan.salehi@stock-solution.de",
    }
    user = await service.get("pouyan.salehi@stock-solution.de")
    assert user.id == "abc-123"
    mock_client.get.assert_called_once_with("/users/pouyan.salehi@stock-solution.de")


@pytest.mark.asyncio
async def test_resolve_to_id_returns_id_for_email(service, mock_client):
    mock_client.get.return_value = {
        "id": "abc-123",
        "displayName": "Pouyan Salehi",
        "mail": "pouyan.salehi@stock-solution.de",
        "userPrincipalName": "pouyan.salehi@stock-solution.de",
    }
    user_id = await service.resolve_to_id("pouyan.salehi@stock-solution.de")
    assert user_id == "abc-123"


@pytest.mark.asyncio
async def test_resolve_to_id_passes_through_uuid(service, mock_client):
    """If input is already a UUID, skip the API call and return as-is."""
    user_id = await service.resolve_to_id("abc-123-def-456")
    mock_client.get.assert_not_called()
    assert user_id == "abc-123-def-456"
