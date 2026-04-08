import typer
from ms_planner.cli.plans import plans_app
from ms_planner.cli.buckets import buckets_app
from ms_planner.cli.tasks import tasks_app

app = typer.Typer(name="planner", help="Microsoft Planner CLI")
app.add_typer(plans_app, name="plans")
app.add_typer(buckets_app, name="buckets")
app.add_typer(tasks_app, name="tasks")

if __name__ == "__main__":
    app()
