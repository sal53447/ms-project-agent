import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings

groups_app = typer.Typer(help="List M365 groups")
console = Console()


def _get_client() -> GraphClient:
    settings = Settings()
    return GraphClient(token_factory=lambda: get_token(settings))


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@groups_app.command("list")
def list_groups(
    filter: Annotated[
        str | None,
        typer.Option("--filter", help="OData filter (e.g. \"displayName eq 'My Team'\")"),
    ] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List M365 groups in the tenant. Use --filter to search by name."""
    client = _get_client()

    async def _fetch():
        # Only list M365 groups (unified), not security groups
        path = "/groups?$filter=groupTypes/any(c:c eq 'Unified')&$select=id,displayName,description,mail&$top=100"
        if filter:
            path = f"/groups?$filter={filter} and groupTypes/any(c:c eq 'Unified')&$select=id,displayName,description,mail&$top=100"
        all_groups = []
        while path:
            data = await client.get(path)
            all_groups.extend(data.get("value", []))
            next_link = data.get("@odata.nextLink", "")
            # nextLink is an absolute URL; strip the base to get a relative path
            if next_link:
                path = next_link.replace("https://graph.microsoft.com/v1.0", "")
            else:
                path = None
        return all_groups

    groups = _run(_fetch())

    if json:
        console.print(json_lib.dumps(groups, indent=2, default=str))
        return

    table = Table(title="M365 Groups")
    table.add_column("ID")
    table.add_column("Display Name")
    table.add_column("Mail")
    table.add_column("Description")
    for g in groups:
        table.add_row(
            g.get("id", ""),
            g.get("displayName", ""),
            g.get("mail", ""),
            (g.get("description") or "")[:60],
        )
    console.print(table)
