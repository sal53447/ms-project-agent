import asyncio
import json as json_lib
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ms_planner.auth import get_token
from ms_planner.client import GraphClient
from ms_planner.config import Settings
from ms_planner.services.snapshot import SnapshotService

snapshot_app = typer.Typer(help="Manage Planner state snapshots")
console = Console()


def _get_snapshot_service() -> SnapshotService:
    settings = Settings()
    client = GraphClient(token_factory=lambda: get_token(settings))
    return SnapshotService(client)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@snapshot_app.command("take")
def take(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    project_dir: Annotated[str, typer.Option("--project-dir", help="Project directory path")],
):
    """Fetch current Planner state and write planner-snapshot.json.
    Archives the previous snapshot first if one exists.
    """
    svc = _get_snapshot_service()
    path = Path(project_dir)
    existing = svc.load(path)
    if existing is not None:
        svc.archive(path)
        console.print("[dim]Archived previous snapshot.[/dim]")
    tasks = _run(svc.fetch(plan_id))
    svc.save(path, plan_id, tasks)
    console.print(f"[green]Snapshot written:[/green] {len(tasks)} tasks captured.")


@snapshot_app.command("diff")
def diff(
    plan_id: Annotated[str, typer.Option("--plan-id", help="Plan ID")],
    project_dir: Annotated[str, typer.Option("--project-dir", help="Project directory path")],
):
    """Compare current Planner state against the existing snapshot.
    Outputs a JSON delta report. If no snapshot exists, reports initial baseline.
    """
    svc = _get_snapshot_service()
    path = Path(project_dir)
    existing = svc.load(path)
    current_tasks = _run(svc.fetch(plan_id))
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if existing is None:
        console.print(
            json_lib.dumps(
                {
                    "status": "initial_baseline",
                    "message": "No prior snapshot found. Current Planner state is the baseline.",
                    "as_of": as_of,
                    "task_count": len(current_tasks),
                },
                indent=2,
            )
        )
        return

    delta = svc.diff(existing, current_tasks, as_of=as_of)
    console.print(json_lib.dumps(delta.model_dump(), indent=2))
