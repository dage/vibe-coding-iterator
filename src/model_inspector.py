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
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import queue
from datetime import datetime

# Check dependencies first
from check_deps import ensure_dependencies
ensure_dependencies(["rich", "deepctl", "requests"])

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich import box
from typing import Any

_FIELDS = [
    "index", "id", "token_cost", "code_hint", "vision_hint",
    "downloads", "likes", "created", "updated", "license"
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

def _get_code_capability(mid: str, hf: dict) -> str:
    """Determine if model has code generation capabilities"""
    tags = hf.get("tags", [])
    pipeline = hf.get("pipeline_tag") or ""
    
    # Check for code-related tags
    code_tags = ["code", "coder", "sql", "programming", "code-generation"]
    vision_tags = ["vision", "multimodal", "image", "ocr", "vlm", "image-to-text"]
    
    # Check pipeline tags
    if any(tag in pipeline.lower() for tag in code_tags):
        return "💻"
    
    # Check model tags
    if any(tag.lower() in code_tags for tag in tags):
        return "💻"
    
    # Check for vision capabilities (exclude from code)
    if any(tag.lower() in vision_tags for tag in tags):
        return ""
    
    # Check README for code-related content
    try:
        readme_url = f"https://huggingface.co/{mid}/raw/main/README.md"
        readme_text = requests.get(readme_url, timeout=5).text.lower()
        
        # Look for code-related keywords
        code_keywords = [
            "code generation", "programming", "human-eval", "pass@", "swe-bench",
            "code completion", "code synthesis", "software engineering", "coding",
            "program synthesis", "code understanding", "code analysis"
        ]
        
        if any(keyword in readme_text for keyword in code_keywords):
            return "💻"
            
    except Exception:
        pass
    
    return ""

def _get_vision_capability(mid: str, hf: dict) -> str:
    """Determine if model has vision/multimodal capabilities"""
    tags = hf.get("tags", [])
    pipeline = hf.get("pipeline_tag") or ""
    
    # Check for vision-related tags
    vision_tags = ["vision", "multimodal", "image", "ocr", "vlm", "image-to-text", "image-generation"]
    
    # Check pipeline tags
    if any(tag in pipeline.lower() for tag in vision_tags):
        return "👁️"
    
    # Check model tags
    if any(tag.lower() in vision_tags for tag in tags):
        return "👁️"
    
    # Check README for vision-related content
    try:
        readme_url = f"https://huggingface.co/{mid}/raw/main/README.md"
        readme_text = requests.get(readme_url, timeout=5).text.lower()
        
        # Look for vision-related keywords
        vision_keywords = [
            "vision", "multimodal", "image", "ocr", "visual", "image-to-text",
            "image understanding", "computer vision", "visual language model",
            "image generation", "image captioning", "visual reasoning"
        ]
        
        if any(keyword in readme_text for keyword in vision_keywords):
            return "👁️"
            
    except Exception:
        pass
    
    return ""

def _get_detailed_model_info(mid: str, index: int) -> dict:
    """Get detailed information about a specific model"""
    console = Console()
    
    console.print(f"\n[bold cyan]Detailed Information for Model #{index}: {mid}[/bold cyan]")
    console.print("=" * 80)
    
    # Get HuggingFace metadata
    console.print("[yellow]Fetching HuggingFace metadata...[/yellow]")
    hf = _hf_meta(mid)
    
    if not hf:
        console.print("[red]✗ Failed to fetch model metadata[/red]")
        return {}
    
    # Get DeepInfra pricing
    console.print("[yellow]Fetching DeepInfra pricing...[/yellow]")
    token_cost = _deepinfra_price(mid)
    
    # Get README content
    console.print("[yellow]Fetching README content...[/yellow]")
    readme_content = ""
    try:
        readme_url = f"https://huggingface.co/{mid}/raw/main/README.md"
        readme_content = requests.get(readme_url, timeout=10).text
    except Exception:
        readme_content = "Unable to fetch README"
    
    # Create detailed info table
    table = Table(title=f"Model #{index}: {mid}", box=box.ROUNDED)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="white")
    
    # Basic info
    table.add_row("Model ID", mid)
    table.add_row("Token Cost", f"${token_cost}/M tokens")
    table.add_row("Downloads", str(hf.get("downloads", "—")))
    table.add_row("Likes", f"❤️ {hf.get('likes', '—')}")
    table.add_row("Created", hf.get("createdAt", "—"))
    table.add_row("Updated", hf.get("lastModified", "—"))
    table.add_row("License", hf.get("license", "—"))
    table.add_row("Pipeline Tag", hf.get("pipeline_tag", "—"))
    table.add_row("Model Type", hf.get("model_type", "—"))
    
    # Capabilities
    code_hint = _get_code_capability(mid, hf)
    vision_hint = _get_vision_capability(mid, hf)
    capabilities = []
    if code_hint:
        capabilities.append("Code Generation")
    if vision_hint:
        capabilities.append("Vision/Multimodal")
    if not capabilities:
        capabilities.append("Text Generation")
    
    table.add_row("Capabilities", ", ".join(capabilities))
    
    # Tags
    tags = hf.get("tags", [])
    if tags:
        table.add_row("Tags", ", ".join(tags[:10]) + ("..." if len(tags) > 10 else ""))
    
    console.print(table)
    
    # Show README excerpt
    if readme_content and readme_content != "Unable to fetch README":
        console.print(f"\n[bold cyan]README Excerpt:[/bold cyan]")
        console.print("=" * 80)
        # Show first 500 characters of README
        excerpt = readme_content[:500]
        if len(readme_content) > 500:
            excerpt += "..."
        console.print(Panel(excerpt, title="README.md", border_style="blue"))
    
    return {
        "index": index,
        "id": mid,
        "token_cost": token_cost,
        "hf_metadata": hf,
        "readme_content": readme_content
    }

def _process_model(args: tuple) -> dict:
    """Process a single model - used by worker threads"""
    idx, mid, worker_id, progress_callback = args
    
    try:
        # Step 1: Get HuggingFace metadata
        progress_callback(worker_id, "🔄", f"Querying HuggingFace API for {mid[:30]}{'...' if len(mid) > 30 else ''}")
        hf = _hf_meta(mid)
        
        # Step 2: Get DeepInfra pricing
        progress_callback(worker_id, "💰", f"Getting DeepInfra pricing for {mid[:30]}{'...' if len(mid) > 30 else ''}")
        token_cost = _deepinfra_price(mid)
        
        # Step 3: Get capabilities
        progress_callback(worker_id, "🔍", f"Analyzing capabilities for {mid[:30]}{'...' if len(mid) > 30 else ''}")
        code_hint = _get_code_capability(mid, hf)
        vision_hint = _get_vision_capability(mid, hf)
        
        # Step 4: Complete
        progress_callback(worker_id, "✅", f"Completed processing {mid[:30]}{'...' if len(mid) > 30 else ''}")
        
        # Create record
        rec = {
            "index": idx,
            "id": mid,
            "token_cost": token_cost,
            "code_hint": code_hint,
            "vision_hint": vision_hint,
            "downloads": hf.get("downloads", "—"),
            "likes": hf.get("likes", "—"),
            "created": (hf.get("createdAt") or "")[:10],
            "updated": (hf.get("lastModified") or "")[:10],
            "license": hf.get("license", "—")
        }
        
        return {"worker_id": worker_id, "status": "✅", "model": mid, "record": rec}
        
    except Exception as e:
        progress_callback(worker_id, "❌", f"Failed processing {mid[:30]}{'...' if len(mid) > 30 else ''} - {str(e)}")
        return {"worker_id": worker_id, "status": "❌", "model": mid, "error": str(e)}

class UnifiedDisplay:
    """Single Live display showing progress bar and worker status lines"""
    
    def __init__(self, num_workers: int, total_subtasks: int):
        self.num_workers = num_workers
        self.total_subtasks = total_subtasks
        self.worker_statuses = {i: "⏳ Idle" for i in range(num_workers)}
        self.completed_subtasks = 0
        self.lock = Lock()
        
        # Create progress bar
        self.progress = Progress(
            BarColumn(bar_width=None, complete_style="white", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            transient=False
        )
        self.progress_task = self.progress.add_task("", total=total_subtasks)
        
        # Create worker progress bars with spinners
        self.worker_progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            console=None,
            transient=False
        )
        
        # Add worker tasks
        self.worker_tasks = {}
        for i in range(num_workers):
            task_id = self.worker_progress.add_task(f"Worker {i+1}: Idle", total=None)
            self.worker_tasks[i] = task_id
    
    def update_worker(self, worker_id: int, icon: str, message: str):
        """Update worker status and progress"""
        with self.lock:
            self.worker_statuses[worker_id] = f"{icon} {message}"
            # Update worker progress description with both spinner and task icon
            if icon in ["🔄", "💰", "📝"]:
                # Active work - show spinner + task icon
                display_text = f"{icon} {message}"
            elif icon == "❌":
                # Failed - show red text
                display_text = f"[red]{icon} {message}[/red]"
            elif icon == "⏳":
                # Waiting/backoff - show hourglass
                display_text = f"{icon} {message}"
            else:
                # Completed - show checkmark
                display_text = f"{icon} {message}"
            
            self.worker_progress.update(self.worker_tasks[worker_id], description=display_text)
            # Increment progress for each subtask (3 per model)
            if icon in ["🔄", "💰", "📝"]:
                self.completed_subtasks += 1
                self.progress.update(self.progress_task, completed=self.completed_subtasks)
    
    def __rich__(self) -> Any:
        """Render the complete display"""
        # Return group with progress bar and worker progress
        return Group(self.progress, self.worker_progress)

# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--format", choices=["json", "markdown-table"], default="json")
    ap.add_argument("--limit", type=int, help="Limit number of models to process")
    ap.add_argument("--workers", type=int, default=10, help="Number of worker threads")
    ap.add_argument("--query", type=str, help="Query specific model by index (e.g., '?5')")
    args = ap.parse_args()

    console = Console()
    
    try:
        model_list = _deepinfra_list()
    except subprocess.CalledProcessError as e:
        console.print("[red]✗ Failed to list models from DeepInfra[/red]", file=sys.stderr)
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        console.print("[dim]Ensure deepctl is installed and your API key is configured[/dim]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        console.print("[red]✗ Unexpected error while listing models[/red]", file=sys.stderr)
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)
    
    if not model_list:
        console.print("[yellow]⚠ No models found[/yellow]", file=sys.stderr)
        sys.exit(1)
    
    # Handle query for specific model
    if args.query and args.query.startswith('?'):
        try:
            index = int(args.query[1:])
            if index < 1 or index > len(model_list):
                console.print(f"[red]✗ Invalid model index: {index}. Available range: 1-{len(model_list)}[/red]")
                sys.exit(1)
            
            model_id = model_list[index - 1]  # Convert to 0-based index
            _get_detailed_model_info(model_id, index)
            return
            
        except ValueError:
            console.print(f"[red]✗ Invalid query format: {args.query}. Use '?<number>' (e.g., '?5')[/red]")
            sys.exit(1)
    
    if args.limit:
        model_list = model_list[:args.limit]
    
    records = []
    
    # Print initial message
    console.print("Building model catalogue...")
    
    # Calculate total subtasks (3 per model)
    total_subtasks = len(model_list) * 3
    
    # Create unified display
    display = UnifiedDisplay(args.workers, total_subtasks)
    
    # Progress callback function for workers
    def update_progress(worker_id: int, icon: str, message: str):
        display.update_worker(worker_id, icon, message)
    
    # Use Live display for real-time updates
    with Live(display, refresh_per_second=4, console=console):
        # Prepare work items
        work_items = []
        for idx, mid in enumerate(model_list, 1):
            worker_id = (idx - 1) % args.workers
            work_items.append((idx, mid, worker_id, update_progress))
        
        # Process models in parallel
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(_process_model, item): item for item in work_items}
            
            # Process completed tasks
            for future in as_completed(future_to_item):
                result = future.result()
                worker_id = result["worker_id"]
                
                # Add record if successful
                if result["status"] == "✅":
                    records.append(result["record"])
    
    # Sort records by index to maintain order
    records.sort(key=lambda x: x["index"])

    Path(args.output).write_text(json.dumps(records, indent=2))

    if args.format == "markdown-table":
        from rich.table import Table
        from rich import box
        
        # Create table with UI guidelines styling
        table = Table(
            title=f"Available Models ({len(records)} models) - Use '?<index>' for detailed info",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            width=None
        )
        
        # Add columns with appropriate styling - compact table
        table.add_column("Index", justify="right", style="bright_blue")
        table.add_column("Model", no_wrap=True, style="cyan")
        table.add_column("$/M", justify="right", style="bright_blue")
        table.add_column("Code", justify="center", style="green")
        table.add_column("Vision", justify="center", style="yellow")
        table.add_column("Downloads", justify="right", style="bright_blue")
        table.add_column("❤️", justify="right", style="red")
        table.add_column("Created", style="dim")
        
        # Add rows
        for r in records:
            row_data = [
                str(r["index"]),
                r["id"],
                str(r["token_cost"]),
                r["code_hint"],
                r["vision_hint"],
                str(r["downloads"]),
                str(r["likes"]),
                r["created"]
            ]
            table.add_row(*row_data)
        
        console.print(table)

if __name__ == "__main__":
    main() 