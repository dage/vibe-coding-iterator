from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import random, string

ROOT = Path("storage")
RUNS = ROOT / "runs"


def run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    suf = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return f"{ts}_{suf}"


def run_dir(rid: str) -> Path:
    return RUNS / rid


def screenshots_dir(rid: str) -> Path:
    d = run_dir(rid) / "screenshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def workspace_dir(rid: str) -> Path:
    d = run_dir(rid) / "workspace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def events_path(rid: str) -> Path:
    run_dir(rid).mkdir(parents=True, exist_ok=True)
    return run_dir(rid) / "events.jsonl"


def snap_path(rid: str, iteration: int) -> Path:
    return screenshots_dir(rid) / f"snap_{iteration}.png"


