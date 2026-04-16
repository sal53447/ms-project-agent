import asyncio
import json as json_lib
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.tasks import TaskService
from ms_planner.services.users import UserService

tasks_app = typer.Typer(help="Manage tasks")
console = Console()


def _get_task_service() -> TaskService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return TaskService(client)


def _get_user_service() -> UserService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return UserService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@tasks_app.command("list")
def list_tasks(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all tasks in a plan."""
    service = _get_task_service()
    tasks = _run(service.list(plan_id))

    if json:
        console.print(json_lib.dumps([t.model_dump() for t in tasks], indent=2, default=str))
        return

    table = Table(title="Tasks")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Progress")
    table.add_column("Priority")
    table.add_column("Due Date")
    for t in tasks:
        progress = f"{t.percent_complete}%"
        due = str(t.due_date_time.date()) if t.due_date_time else ""
        table.add_row(t.id, t.title, progress, str(t.priority), due)
    console.print(table)


@tasks_app.command("get")
def get_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get a specific task."""
    service = _get_task_service()
    task = _run(service.get(task_id))

    if json:
        console.print(json_lib.dumps(task.model_dump(), indent=2, default=str))
        return

    table = Table(title="Task")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", task.id)
    table.add_row("Title", task.title)
    table.add_row("Plan ID", task.plan_id or "")
    table.add_row("Bucket ID", task.bucket_id or "")
    table.add_row("Progress", f"{task.percent_complete}%")
    table.add_row("Priority", str(task.priority))
    table.add_row("Start", str(task.start_date_time) if task.start_date_time else "")
    table.add_row("Due", str(task.due_date_time) if task.due_date_time else "")
    table.add_row("Assignees", ", ".join(task.assignments.keys()) if task.assignments else "")
    console.print(table)


@tasks_app.command("create")
def create_task(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    title: Annotated[str, typer.Option("--title", help="Task title")],
    bucket_id: Annotated[str | None, typer.Option("--bucket-id", help="Bucket ID")] = None,
    assign: Annotated[list[str] | None, typer.Option("--assign", help="User IDs to assign")] = None,
    description: Annotated[str | None, typer.Option("--description", help="Task description")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Create a new task."""
    service = _get_task_service()
    task = _run(service.create(plan_id=plan_id, title=title, bucket_id=bucket_id, assignments=assign))
    if description is not None:
        _run(service.update_details(task.id, description=description))

    if json:
        console.print(json_lib.dumps(task.model_dump(), indent=2, default=str))
        return

    console.print(f"[green]Created task:[/green] {task.id} — {task.title}")


@tasks_app.command("update")
def update_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    progress: Annotated[int | None, typer.Option("--progress", help="Percent complete (0, 50, 100)")] = None,
    priority: Annotated[int | None, typer.Option("--priority", help="Priority (0-10, lower=higher)")] = None,
    title: Annotated[str | None, typer.Option("--title", help="New title")] = None,
    bucket_id: Annotated[str | None, typer.Option("--bucket-id", help="Move task to a different bucket")] = None,
    due_date: Annotated[str | None, typer.Option("--due-date", help="Due date (YYYY-MM-DD)")] = None,
    start_date: Annotated[str | None, typer.Option("--start-date", help="Start date (YYYY-MM-DD)")] = None,
    description: Annotated[str | None, typer.Option("--description", help="Task description / notes")] = None,
    assign: Annotated[list[str] | None, typer.Option("--assign", help="User IDs/emails to add as assignees")] = None,
    unassign: Annotated[list[str] | None, typer.Option("--unassign", help="User IDs/emails to remove as assignees")] = None,
):
    """Update a task."""
    service = _get_task_service()
    kwargs = {}
    if progress is not None:
        kwargs["percent_complete"] = progress
    if priority is not None:
        kwargs["priority"] = priority
    if title is not None:
        kwargs["title"] = title
    if bucket_id is not None:
        kwargs["bucket_id"] = bucket_id
    if due_date is not None:
        kwargs["due_date_time"] = f"{due_date}T00:00:00Z"
    if start_date is not None:
        kwargs["start_date_time"] = f"{start_date}T00:00:00Z"
    if assign is not None or unassign is not None:
        user_svc = _get_user_service()
        assignments = {}
        for a in (assign or []):
            uid = _run(user_svc.resolve_to_id(a))
            assignments[uid] = {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"}
        for a in (unassign or []):
            uid = _run(user_svc.resolve_to_id(a))
            assignments[uid] = None
        kwargs["assignments"] = assignments
    if not kwargs and description is None:
        console.print("[yellow]No updates specified[/yellow]")
        return
    if kwargs:
        _run(service.update(task_id, **kwargs))
    if description is not None:
        _run(service.update_details(task_id, description=description))
    console.print(f"[green]Updated task:[/green] {task_id}")


@tasks_app.command("delete")
def delete_task(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
):
    """Delete a task."""
    service = _get_task_service()
    _run(service.delete(task_id))
    console.print(f"[red]Deleted task:[/red] {task_id}")


@tasks_app.command("details")
def task_details(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Get task details (description, checklist, attachments)."""
    service = _get_task_service()
    details = _run(service.get_details(task_id))

    if json:
        console.print(json_lib.dumps(details.model_dump(), indent=2, default=str))
        return

    console.print(f"[bold]Description:[/bold] {details.description}")
    if details.checklist:
        console.print("\n[bold]Checklist:[/bold]")
        for item_id, item in details.checklist.items():
            check = "[x]" if item.is_checked else "[ ]"
            console.print(f"  {check} {item.title}  ({item_id})")
    if details.references:
        console.print("\n[bold]Attachments:[/bold]")
        for url, ref in details.references.items():
            console.print(f"  {ref.alias or 'Untitled'}: {url}")


@tasks_app.command("checklist-add")
def checklist_add(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    item: Annotated[str, typer.Option("--item", help="Checklist item text")],
):
    """Add a checklist item to a task."""
    import uuid

    service = _get_task_service()
    item_id = str(uuid.uuid4())
    _run(
        service.update_details(
            task_id,
            checklist={item_id: {"@odata.type": "microsoft.graph.plannerChecklistItem", "title": item}},
        )
    )
    console.print(f"[green]Added checklist item:[/green] {item}")


@tasks_app.command("checklist-remove")
def checklist_remove(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    item_id: Annotated[str, typer.Option("--item-id", help="Checklist item ID")],
):
    """Remove a checklist item from a task."""
    service = _get_task_service()
    _run(service.update_details(task_id, checklist={item_id: None}))
    console.print(f"[red]Removed checklist item:[/red] {item_id}")


@tasks_app.command("attach")
def attach(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    url: Annotated[str, typer.Option("--url", help="URL to attach")],
    alias: Annotated[str, typer.Option("--alias", help="Display name")] = "",
):
    """Attach a URL reference to a task."""
    import urllib.parse

    service = _get_task_service()
    encoded_url = urllib.parse.quote(url, safe="")
    _run(
        service.update_details(
            task_id,
            references={
                encoded_url: {
                    "@odata.type": "microsoft.graph.plannerExternalReference",
                    "alias": alias,
                    "type": "Other",
                }
            },
        )
    )
    console.print(f"[green]Attached:[/green] {alias or url}")
