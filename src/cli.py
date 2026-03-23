import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

app = typer.Typer(help="AI Delivery Risk & Requirement Analyzer (console edition).")


@app.command()
def ingest(data_dir: Path = typer.Argument(..., exists=True, dir_okay=True, readable=True)):
    """
    Placeholder ingest command.

    Loads curated documents, chunks, embeds, and persists an index.
    """
    print(f"[yellow]Ingest not yet implemented.[/yellow] Would read from: {data_dir}")


@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Requirement text input."),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", exists=True, dir_okay=False, readable=True, help="Path to a file."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", dir_okay=False, writable=True, help="Save JSON output to file."
    ),
):
    """
    Placeholder analysis command.

    Accepts inline text or file input and would return a structured clarification report.
    """
    if not text and not file:
        raise typer.BadParameter("Provide either --text or --file.")

    requirement = text
    if file:
        requirement = file.read_text(encoding="utf-8")

    payload = {"message": "Analyze not yet implemented", "input": requirement}
    rendered = json.dumps(payload, indent=2)
    print(rendered)

    if output:
        output.write_text(rendered, encoding="utf-8")
        print(f"[green]Wrote placeholder output to {output}[/green]")


@app.command()
def eval(fixtures: Path = typer.Argument(..., exists=True, dir_okay=True, readable=True)):
    """Placeholder evaluation harness runner."""
    print(f"[yellow]Eval not yet implemented.[/yellow] Would load fixtures from: {fixtures}")


if __name__ == "__main__":
    app()
