from pathlib import Path
from typing import Optional

import typer
from rich import print

from ai_analyzer.analysis import ContextItem, run_analysis
from ai_analyzer.config import load_embed_config, load_llm_config
from ai_analyzer.embeddings import build_embed_fn
from ai_analyzer.ingest import ingest_corpus_with_embed
from ai_analyzer.logging_utils import save_run
from ai_analyzer.retrieval import embed_query, load_index, similarity_search

app = typer.Typer(help="AI Delivery Risk & Requirement Analyzer (console edition).")


@app.command()
def ingest(
    data_dir: Path = typer.Argument(Path("data/curated"), exists=True, dir_okay=True, readable=True),
    index_dir: Path = typer.Option(Path("data/index"), "--index-dir", "-i", dir_okay=True, writable=True),
    force: bool = typer.Option(False, "--force", "-f", help="Rebuild even if an index already exists."),
):
    """
    Load curated documents, chunk, embed, and persist a FAISS index.
    """
    index_path = index_dir / "index.faiss"
    if index_path.exists() and not force:
        print(f"[yellow]Index already exists at {index_path}. Use --force to rebuild.[/yellow]")
        return

    embed_config = load_embed_config()
    embed_fn = build_embed_fn(embed_config)
    try:
        ingest_corpus_with_embed(data_dir, index_dir, embed_fn)
    except ValueError as exc:
        print(f"[red]Ingest failed:[/red] {exc}")
        raise typer.Exit(code=1)

    print(
        f"[green]Ingest complete.[/green] Provider: {embed_config.provider}. "
        f"Index saved to {index_dir}"
    )


@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Requirement text input."),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", exists=True, dir_okay=False, readable=True, help="Path to a file."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", dir_okay=False, writable=True, help="Save JSON output to file."
    ),
    no_reflect: bool = typer.Option(
        False, "--no-reflect", help="Skip the reflection pass to save tokens/time."
    ),
    index_dir: Path = typer.Option(Path("data/index"), "--index-dir", "-i", dir_okay=True, readable=True),
):
    """
    Retrieve context for a requirement and run full analysis, returning a structured report.
    """
    if not text and not file:
        raise typer.BadParameter("Provide either --text or --file.")

    requirement = text
    if file:
        requirement = file.read_text(encoding="utf-8")

    llm_config = load_llm_config()
    embed_config = load_embed_config()
    embed_fn = build_embed_fn(embed_config)
    try:
        index, docstore = load_index(index_dir)
    except FileNotFoundError:
        print(
            "[red]Index not found.[/red] Run "
            f"[cyan]ai-analyze ingest {index_dir}[/cyan] first (or specify --index-dir)."
        )
        raise typer.Exit(code=1)
    query_vec = embed_query(requirement, embed_fn)
    retrieved = similarity_search(query_vec, index, docstore, top_k=5)

    contexts = [ContextItem(text=r.text, metadata=r.metadata, score=r.score) for r in retrieved]
    report = run_analysis(requirement, contexts, llm_config, enable_reflection=not no_reflect)
    rendered = report.model_dump_json(indent=2)
    print(rendered)

    if output:
        output.write_text(rendered, encoding="utf-8")
        print(f"[green]Wrote output to {output}[/green]")
    else:
        run_path = save_run(
            {
                "input": requirement,
                "provider": llm_config.provider,
                "model": llm_config.model,
                "embed_provider": embed_config.provider,
                "retrieved": [c.metadata for c in contexts],
                "report": report.model_dump(),
            }
        )
        print(f"[blue]Logged run to {run_path}[/blue]")


@app.command()
def eval(fixtures: Path = typer.Argument(..., exists=True, dir_okay=True, readable=True)):
    """Placeholder evaluation harness runner."""
    print(f"[yellow]Eval not yet implemented.[/yellow] Would load fixtures from: {fixtures}")


if __name__ == "__main__":
    app()
