# src/ms_planner/cli/main.py
import typer
from rich.console import Console

from ms_planner.cli.groups import groups_app
from ms_planner.cli.plans import plans_app
from ms_planner.cli.buckets import buckets_app
from ms_planner.cli.tasks import tasks_app
from ms_planner.cli.snapshot import snapshot_app
from ms_planner.exceptions import (
    PlannerConflictError,
    PlannerForbiddenError,
    PlannerNotFoundError,
    PlannerThrottledError,
)

app = typer.Typer(
    name="planner",
    help="Microsoft Planner CLI — manage plans, tasks, and buckets via Graph API",
)
app.add_typer(groups_app, name="groups")
app.add_typer(plans_app, name="plans")
app.add_typer(buckets_app, name="buckets")
app.add_typer(tasks_app, name="tasks")
app.add_typer(snapshot_app, name="snapshot")

console = Console(stderr=True)


@app.callback()
def main():
    """Microsoft Planner CLI."""


def run():
    try:
        app()
    except PlannerNotFoundError as e:
        console.print(f"[red]Not found:[/red] {e}")
        raise typer.Exit(1)
    except PlannerForbiddenError as e:
        console.print(f"[red]Access denied:[/red] {e}")
        console.print("[dim]Check that admin consent was granted for the app permissions.[/dim]")
        raise typer.Exit(1)
    except PlannerConflictError as e:
        console.print(f"[red]Conflict:[/red] {e}")
        console.print("[dim]The resource was modified by another user. Try again.[/dim]")
        raise typer.Exit(1)
    except PlannerThrottledError as e:
        console.print(f"[red]Rate limited:[/red] {e}")
        console.print("[dim]Too many requests. Wait a moment and try again.[/dim]")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]Auth error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    run()
