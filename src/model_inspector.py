#!/usr/bin/env python3
# src/model_inspector.py

"""
model_inspector.py  – gathers DeepInfra + HuggingFace metadata and prints
either JSON or a markdown table (one row per model).

• ZERO file I/O – caller decides what to do with the JSON.
• Internal helpers are prefixed with "_".
"""
import argparse, json, subprocess, sys, time, requests
from pathlib import Path

# Check dependencies first
from check_deps import ensure_dependencies
ensure_dependencies(["rich", "deepctl", "requests"])

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

_FIELDS = [
    "index", "id", "token_cost", "capabilities",
    "downloads", "likes", "created", "updated", "license", "notes"
]

# ---------- internal helpers ----------

def _run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True)

def _deepinfra_list() -> list[str]:
    raw = _run("deepctl model list")
    models = []
    for line in raw.splitlines():
        if line.startswith("text-generation:"):
            model_id = line.split(":", 1)[1].strip()
            models.append(model_id)
    return models

def _deepinfra_price(mid: str) -> float:
    info = _run(f"deepctl model info --model {mid}")
    for line in info.splitlines():
        if line.startswith("pricing:"):
            pricing = line.split(":", 1)[1].strip()
            per_k = float(pricing.split("$")[1].split("/")[0])   # e.g. 0.0006
            return round(per_k * 1000, 4)                        # → $/M tokens
    return 0.0  # fallback

def _hf_meta(mid: str) -> dict:
    url = f"https://huggingface.co/api/models/{mid}"
    for _ in range(3):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 404:
                return {}
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep(2)
    return {}

def _caps(hf: dict) -> str:
    tags = hf.get("tags", [])
    pipeline = hf.get("pipeline_tag") or ""
    mtype = hf.get("model_type") or hf.get("library_name") or ""
    out = ", ".join(dict.fromkeys([pipeline, mtype, *tags]))     # uniq-preserve
    # Limit to 5 most relevant tags for table display
    if len(out) > 60:
        parts = out.split(", ")
        if len(parts) > 5:
            out = ", ".join(parts[:5]) + "…"
        else:
            out = out[:57] + "…"
    return out

_GREPS = (
    "code", "coder", "sql", "human-eval", "pass@", "vision", "multimodal",
    "image", "ocr", "vlm", "benchmark", "leaderboard"
)

def _notes(mid: str) -> str:
    try:
        txt = requests.get(f"https://huggingface.co/{mid}/raw/main/README.md",
                           timeout=5).text.lower()
        lines = [ln.strip() for ln in txt.splitlines()
                 if any(g in ln for g in _GREPS)]
        notes = " | ".join(lines[:2])
        # Truncate notes for table display
        if len(notes) > 40:
            notes = notes[:37] + "…"
        return notes
    except Exception:
        return ""

# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--format", choices=["json", "markdown-table"], default="json")
    ap.add_argument("--limit", type=int, help="Limit number of models to process")
    args = ap.parse_args()

    model_list = _deepinfra_list()
    
    if args.limit:
        model_list = model_list[:args.limit]
    
    records = []
    
    console = Console()
    
    # Print initial message
    console.print("Building model catalogue (this may take a moment)...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, complete_style="white", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        # Add overall progress task
        overall_task = progress.add_task("Building model catalogue", total=len(model_list))
        
        for idx, mid in enumerate(model_list, 1):
            # Update overall progress - just show progress without redundant description
            progress.update(overall_task, completed=idx-1)
            
            # Add individual model task
            model_task = progress.add_task(f"Processing {mid}", total=None)
            
            # Update task description for each step
            progress.update(model_task, description=f"Processing {mid} - Getting HuggingFace metadata...")
            hf = _hf_meta(mid)
            
            progress.update(model_task, description=f"Processing {mid} - Getting pricing info...")
            token_cost = _deepinfra_price(mid)
            
            progress.update(model_task, description=f"Processing {mid} - Getting notes...")
            notes = _notes(mid)
            
            # Remove individual model task when done
            progress.remove_task(model_task)
            
            rec = {
                "index": idx,
                "id": mid,
                "token_cost": token_cost,
                "capabilities": _caps(hf),
                "downloads": hf.get("downloads", "—"),
                "likes": hf.get("likes", "—"),
                "created": (hf.get("createdAt") or "")[:10],
                "updated": (hf.get("lastModified") or "")[:10],
                "license": hf.get("license", "—"),
                "notes": notes
            }
            records.append(rec)
        
        # Complete overall progress
        progress.update(overall_task, completed=len(model_list))

    Path(args.output).write_text(json.dumps(records, indent=2))

    if args.format == "markdown-table":
        from rich.table import Table
        from rich import box
        
        # Create table with UI guidelines styling
        table = Table(
            title=f"Available Models ({len(records)} models)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            width=None
        )
        
        # Add columns with appropriate styling - full information for normal terminals
        table.add_column("Index", justify="right", style="bright_blue")
        table.add_column("Model", no_wrap=True, style="cyan")
        table.add_column("$/M", justify="right", style="bright_blue")
        table.add_column("Capabilities")
        table.add_column("Downloads", justify="right", style="bright_blue")
        table.add_column("Likes", justify="right", style="bright_blue")
        table.add_column("Updated")
        table.add_column("Notes")
        
        # Add rows
        for r in records:
            row_data = [
                str(r["index"]),
                r["id"],
                str(r["token_cost"]),
                r["capabilities"],
                str(r["downloads"]),
                str(r["likes"]),
                r["updated"],
                r["notes"]
            ]
            table.add_row(*row_data)
        
        console.print(table)

if __name__ == "__main__":
    main() 