import msal
from ms_planner.config import Settings

_SCOPE = ["https://graph.microsoft.com/.default"]

_app_cache: dict[str, msal.ConfidentialClientApplication] = {}


def _get_app(settings: Settings) -> msal.ConfidentialClientApplication:
    key = f"{settings.tenant_id}:{settings.client_id}"
    if key not in _app_cache:
        _app_cache[key] = msal.ConfidentialClientApplication(
            client_id=settings.client_id,
            client_credential=settings.client_secret,
            authority=f"https://login.microsoftonline.com/{settings.tenant_id}",
        )
    return _app_cache[key]


def get_token(settings: Settings) -> str:
    app = _get_app(settings)
    result = app.acquire_token_silent(_SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=_SCOPE)
    if "access_token" in result:
        return result["access_token"]
    raise RuntimeError(
        result.get("error_description", result.get("error", "Unknown auth error"))
    )
