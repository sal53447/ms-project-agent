import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.buckets import BucketService

buckets_app = typer.Typer(help="Manage buckets")
console = Console()


def _get_bucket_service() -> BucketService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return BucketService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@buckets_app.command("list")
def list_buckets(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all buckets in a plan."""
    service = _get_bucket_service()
    buckets = _run(service.list(plan_id))

    if json:
        console.print(json_lib.dumps([b.model_dump() for b in buckets], indent=2, default=str))
        return

    table = Table(title="Buckets")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Plan ID")
    for b in buckets:
        table.add_row(b.id, b.name, b.plan_id)
    console.print(table)


@buckets_app.command("create")
def create_bucket(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    name: Annotated[str, typer.Option("--name", help="Bucket name")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new bucket in a plan."""
    service = _get_bucket_service()
    bucket = _run(service.create(plan_id, name))

    if json:
        console.print(json_lib.dumps(bucket.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created bucket:[/green] {bucket.id} — {bucket.name}")


@buckets_app.command("delete")
def delete_bucket(
    bucket_id: Annotated[str, typer.Argument(help="Bucket ID")],
):
    """Delete a bucket."""
    service = _get_bucket_service()
    _run(service.delete(bucket_id))
    console.print(f"[red]Deleted bucket:[/red] {bucket_id}")
