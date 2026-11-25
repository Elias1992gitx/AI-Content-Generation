"""
Common utilities for pipeline: caching, hash verification, runs.jsonl telemetry.
"""
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
RUNS_LOG_PATH = BASE_DIR / "runs.jsonl"


def compute_cache_key(*args) -> str:
    """Compute deterministic SHA-256 hash from arguments."""
    payload = json.dumps(args, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def log_run(stage: str, model: str, parameters: dict, seed: int, latency_ms: int, cost_usd: float = 0.0, shot_id: str = None):
    """Append a structured log line to runs.jsonl."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "stage": stage,
        "shot_id": shot_id,
        "model": model,
        "parameters": parameters,
        "seed": seed,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd
    }
    with open(RUNS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{stage.upper()}] Logged run: shot={shot_id} model={model} latency={latency_ms}ms")


def load_storyboard(path: str = None) -> dict:
    """Load and return the central storyboard contract."""
    target_path = Path(path) if path else (BASE_DIR / "storyboard.json")
    with open(target_path, "r", encoding="utf-8") as f:
        return json.load(f)

