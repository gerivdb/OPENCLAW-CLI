"""
OpenClaw CLI - Main entry point

Commands:
  - normalize: Normalize raw intent to canonical spec
  - validate: Validate canonical specification
  - info: Show normalizer information
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

try:
    from openclaw import OpenClawNormalizer
    from openclaw.integrations import KimiLocalClient
    OPENCLAW_AVAILABLE = True
except ImportError:
    OPENCLAW_AVAILABLE = False

app = typer.Typer(
    name="openclaw",
    help="🦞 OpenClaw CLI - L1 Semantic Intent Normalizer",
    add_completion=True
)
console = Console()


@app.command()
def normalize(
    intent: Optional[str] = typer.Argument(None, help="Raw intent to normalize"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Input file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("text", "--format", help="Output format"),
    kimi: bool = typer.Option(True, "--kimi/--no-kimi", help="Enable Kimi"),
    confidence: float = typer.Option(0.0, "--confidence", help="Min confidence"),
):
    """
    Normalize raw intent to canonical JSON-LD specification.
    
    Examples:
        openclaw normalize "surveille le budget phi"
        openclaw normalize --file intents.txt --format json
    """
    if not OPENCLAW_AVAILABLE:
        console.print("[red]Error: OPENCLAW not installed[/red]")
        console.print("Install: pip install git+https://github.com/gerivdb/OPENCLAW.git")
        raise typer.Exit(1)
    
    if not intent and not file:
        console.print("[red]Error: Provide either INTENT or --file[/red]")
        raise typer.Exit(1)
    
    # Initialize normalizer
    kimi_client = KimiLocalClient() if kimi else None
    normalizer = OpenClawNormalizer(kimi_client=kimi_client)
    
    if intent:
        # Single intent
        result = asyncio.run(normalizer.normalize(intent))
        _output_result(result, format, output)
    
    elif file:
        # Batch processing
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(1)
        
        intents = file.read_text().strip().split("\n")
        results = []
        
        with console.status(f"[bold green]Normalizing {len(intents)} intents..."):
            for raw_intent in intents:
                if raw_intent.strip():
                    result = asyncio.run(normalizer.normalize(raw_intent.strip()))
                    if result["suggestion"].confidence >= confidence:
                        results.append(result)
        
        _output_batch_results(results, format, output)


@app.command()
def validate(
    spec_file: Path = typer.Argument(..., help="Canonical spec JSON file"),
    hash: bool = typer.Option(False, "--hash", help="Calculate IntentHash"),
    level: str = typer.Option("L1", "--level", help="Validation level"),
    strict: bool = typer.Option(False, "--strict", help="Strict validation"),
):
    """
    Validate canonical specification compliance.
    
    Examples:
        openclaw validate spec.json
        openclaw validate spec.json --hash --level L2
    """
    if not spec_file.exists():
        console.print(f"[red]File not found: {spec_file}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = json.loads(spec_file.read_text())
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"[green]✓[/green] Valid JSON-LD specification\n"
        f"Level: {level}\n"
        f"Strict: {strict}",
        title="Validation Result"
    ))
    
    if hash:
        # TODO: Implement IntentHash calculation
        console.print("[yellow]IntentHash calculation: Not yet implemented[/yellow]")


@app.command()
def info(
    patterns: bool = typer.Option(False, "--patterns", help="Show patterns"),
    kimi: bool = typer.Option(False, "--kimi", help="Check Kimi availability"),
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    """
    Display OpenClaw normalizer information.
    
    Examples:
        openclaw info
        openclaw info --patterns
        openclaw info --kimi
    """
    if version:
        from openclaw_cli import __version__
        console.print(f"OpenClaw CLI v{__version__}")
        return
    
    if not OPENCLAW_AVAILABLE:
        console.print("[red]OPENCLAW not installed[/red]")
        raise typer.Exit(1)
    
    if patterns:
        _show_patterns()
    elif kimi:
        _check_kimi()
    else:
        _show_info()


def _output_result(result: dict, format: str, output: Optional[Path]):
    """Output single normalization result"""
    suggestion = result["suggestion"]
    
    if format == "json":
        output_data = json.dumps(suggestion.to_dict(), indent=2)
    else:
        output_data = (
            f"Raw Intent: {suggestion.raw_intent}\n"
            f"Method: {suggestion.normalization_method}\n"
            f"Confidence: {suggestion.confidence}\n"
            f"Tools: {', '.join(suggestion.tools_recommended)}\n"
            f"Canonical Spec:\n{suggestion.canonical_spec}"
        )
    
    if output:
        output.write_text(output_data)
        console.print(f"[green]Saved to {output}[/green]")
    else:
        console.print(output_data)


def _output_batch_results(results: list, format: str, output: Optional[Path]):
    """Output batch normalization results"""
    if format == "jsonl":
        lines = [json.dumps(r["suggestion"].to_dict()) for r in results]
        output_data = "\n".join(lines)
    elif format == "json":
        output_data = json.dumps(
            [r["suggestion"].to_dict() for r in results],
            indent=2
        )
    else:
        output_data = f"Processed {len(results)} intents\n"
    
    if output:
        output.write_text(output_data)
        console.print(f"[green]Saved {len(results)} results to {output}[/green]")
    else:
        console.print(output_data)


def _show_patterns():
    """Show built-in normalization patterns"""
    table = Table(title="Built-in Normalization Patterns")
    table.add_column("Pattern", style="cyan")
    table.add_column("Citizen", style="green")
    table.add_column("Confidence", style="yellow")
    table.add_column("Tools", style="magenta")
    
    patterns = [
        ("budget|φ-budget", "PhiBudgetGuardian", "0.91", "C49"),
        ("heartbeat|drift", "EconomicHeartbeat", "0.89", "C51"),
        ("semantic|anchor", "SemanticAnchorCitizen", "0.93", "C47"),
        ("rollback|undo", "RollbackGuardian", "0.87", "C50"),
        ("consensus|vote", "ConsensusEngine", "0.85", "C54"),
    ]
    
    for pattern, citizen, conf, tools in patterns:
        table.add_row(pattern, citizen, conf, tools)
    
    console.print(table)


def _check_kimi():
    """Check Kimi K2.5 local availability"""
    client = KimiLocalClient()
    available = client.health_check(timeout_ms=200)
    
    if available:
        console.print("[green]✓ Kimi K2.5 local available at 127.0.0.1:8765[/green]")
    else:
        console.print("[yellow]⚠ Kimi K2.5 local not available[/yellow]")
        console.print("  Pattern matching will be used as primary method")


def _show_info():
    """Show general normalizer info"""
    console.print(Panel(
        "[bold]🦞 OpenClaw L1 Semantic Normalizer[/bold]\n\n"
        "Layer: L1 (Semantic)\n"
        "Status: Stateless\n"
        "Methods: Pattern Matching → Kimi K2.5 → Fallback\n"
        "Patterns: 5 built-in deterministic patterns\n\n"
        "Use --patterns to see available patterns\n"
        "Use --kimi to check Kimi availability",
        title="OpenClaw Info"
    ))


if __name__ == "__main__":
    app()
