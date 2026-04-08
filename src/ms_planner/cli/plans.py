import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.plans import PlanService

plans_app = typer.Typer(help="Manage plans")
console = Console()


def _get_plan_service() -> PlanService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return PlanService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@plans_app.command("list")
def list_plans(
    group_id: Annotated[str, typer.Option("--group-id", help="M365 Group ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all plans in a group."""
    service = _get_plan_service()
    plans = _run(service.list(group_id))

    if json:
        console.print(json_lib.dumps([p.model_dump() for p in plans], indent=2, default=str))
        return

    table = Table(title="Plans")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Owner")
    for p in plans:
        table.add_row(p.id, p.title, p.owner or "")
    console.print(table)


@plans_app.command("get")
def get_plan(
    plan_id: Annotated[str, typer.Argument(help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get a specific plan."""
    service = _get_plan_service()
    plan = _run(service.get(plan_id))

    if json:
        console.print(json_lib.dumps(plan.model_dump(), indent=2, default=str))
        return

    table = Table(title="Plan")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", plan.id)
    table.add_row("Title", plan.title)
    table.add_row("Owner", plan.owner or "")
    table.add_row("Created", str(plan.created_date_time) if plan.created_date_time else "")
    console.print(table)


@plans_app.command("create")
def create_plan(
    group_id: Annotated[str, typer.Option("--group-id", help="M365 Group ID")],
    title: Annotated[str, typer.Option("--title", help="Plan title")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new plan in a group."""
    service = _get_plan_service()
    plan = _run(service.create(group_id, title))

    if json:
        console.print(json_lib.dumps(plan.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created plan:[/green] {plan.id} — {plan.title}")


@plans_app.command("delete")
def delete_plan(
    plan_id: Annotated[str, typer.Argument(help="Plan ID")],
):
    """Delete a plan."""
    service = _get_plan_service()
    _run(service.delete(plan_id))
    console.print(f"[red]Deleted plan:[/red] {plan_id}")
