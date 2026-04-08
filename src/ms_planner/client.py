import asyncio
from collections.abc import Callable
from typing import Any

import httpx

from ms_planner.exceptions import (
    PlannerConflictError,
    PlannerError,
    PlannerForbiddenError,
    PlannerNotFoundError,
    PlannerThrottledError,
)

_BASE_URL = "https://graph.microsoft.com/v1.0"
_MAX_RETRIES = 3


class GraphClient:
    def __init__(self, token_factory: Callable[[], str]):
        self._token_factory = token_factory
        self._etags: dict[str, str] = {}
        self._http = httpx.AsyncClient(base_url=_BASE_URL, timeout=30.0)

    def get_etag(self, path: str) -> str | None:
        return self._etags.get(path)

    def set_etag(self, path: str, etag: str) -> None:
        self._etags[path] = etag

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token_factory()}"}

    def _store_etag(self, path: str, data: dict[str, Any]) -> None:
        etag = data.get("@odata.etag")
        if etag:
            self._etags[path] = etag

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        headers = self._auth_headers()

        if method in ("PATCH", "DELETE"):
            etag = self._etags.get(path)
            if etag:
                headers["If-Match"] = etag

        for attempt in range(_MAX_RETRIES):
            response = await self._http.request(
                method, path, json=json, headers=headers
            )

            if response.status_code == 429:
                if attempt < _MAX_RETRIES - 1:
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    await asyncio.sleep(retry_after)
                    continue
                raise PlannerThrottledError(
                    "Rate limited after max retries", status_code=429
                )

            if response.status_code in (409, 412):
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(0.5)
                    continue
                raise PlannerConflictError(
                    "ETag conflict after max retries",
                    status_code=response.status_code,
                )

            break

        if response.status_code == 403:
            msg = self._extract_error(response)
            raise PlannerForbiddenError(msg, status_code=403)

        if response.status_code == 404:
            msg = self._extract_error(response)
            raise PlannerNotFoundError(msg, status_code=404)

        if response.status_code >= 400:
            msg = self._extract_error(response)
            raise PlannerError(msg, status_code=response.status_code)

        if response.status_code == 204:
            return None

        data = response.json()
        if method == "GET":
            self._store_etag(path, data)
        return data

    @staticmethod
    def _extract_error(response: httpx.Response) -> str:
        try:
            body = response.json()
            return body.get("error", {}).get("message", response.text)
        except Exception:
            return response.text

    async def get(self, path: str) -> dict[str, Any]:
        result = await self._request("GET", path)
        return result  # type: ignore[return-value]

    async def post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        result = await self._request("POST", path, json=json)
        return result  # type: ignore[return-value]

    async def patch(
        self, path: str, json: dict[str, Any]
    ) -> dict[str, Any] | None:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str) -> None:
        await self._request("DELETE", path)

    async def close(self) -> None:
        await self._http.aclose()
