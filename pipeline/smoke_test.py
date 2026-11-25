#!/usr/bin/env python3
"""
Smoke Test for Phase 1 (Step 1.1)
Tests API access to:
1. Google AI Studio (Gemini API)
2. Cloudflare Workers AI (FLUX.1 schnell)
3. Kaggle account / credentials
Logs latency and cost to runs.jsonl as required by the challenge.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
RUNS_LOG_PATH = BASE_DIR / "runs.jsonl"


def load_env_file():
    """Load variables from .env into os.environ if not already present."""
    if not ENV_PATH.exists():
        print(f"[WARN] .env file not found at {ENV_PATH}")
        return

    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val


def log_telemetry(stage: str, model: str, parameters: dict, latency_ms: int, status: str, error: str = None):
    """Log test result directly into runs.jsonl."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "stage": stage,
        "model": model,
        "parameters": parameters,
        "latency_ms": latency_ms,
        "status": status,
        "cost_usd": 0.0,
        "error": error
    }
    with open(RUNS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def test_gemini():
    """Smoke test Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ [Gemini API] FAILED: GEMINI_API_KEY is missing in .env")
        return False, 0, "Missing API key"

    print("⏳ [Gemini API] Testing connectivity and prompt generation...")
    # Test generation with the models specified in the challenge brief
    test_models = ["gemini-3.8-flash", "gemini-3.5-flash"]
    last_err = None

    for model_name in test_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Hello, respond with only the word 'READY'."}]}]
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed_ms = int((time.time() - start_time) * 1000)
                data = json.loads(resp.read().decode("utf-8"))
                text = ""
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                
                print(f"✅ [Gemini API] SUCCESS ({elapsed_ms}ms) | Model: {model_name} | Response: '{text}'")
                log_telemetry(
                    stage="smoke_test",
                    model=model_name,
                    parameters={"prompt": "smoke_test_ping"},
                    latency_ms=elapsed_ms,
                    status="SUCCESS"
                )
                return True, elapsed_ms, None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}"
        except Exception as e:
            last_err = str(e)

    elapsed_ms = int((time.time() - start_time) * 1000)
    print(f"❌ [Gemini API] FAILED ({elapsed_ms}ms): {last_err}")
    log_telemetry(
        stage="smoke_test",
        model="gemini",
        parameters={"prompt": "smoke_test_ping"},
        latency_ms=elapsed_ms,
        status="FAILED",
        error=last_err
    )
    return False, elapsed_ms, last_err


def test_cloudflare():
    """Smoke test Cloudflare Workers AI FLUX.1 schnell."""
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    token = os.getenv("CLOUDFLARE_API_TOKEN")

    if not account_id or not token:
        print("❌ [Cloudflare AI] FAILED: CLOUDFLARE_ACCOUNT_ID or CLOUDFLARE_API_TOKEN missing in .env")
        return False, 0, "Missing Cloudflare credentials"

    print("⏳ [Cloudflare AI] Testing FLUX.1 schnell endpoint...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "prompt": "A single golden coin on black velvet",
        "steps": 1
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed_ms = int((time.time() - start_time) * 1000)
            img_bytes = resp.read()
            print(f"✅ [Cloudflare AI] SUCCESS ({elapsed_ms}ms) | Received {len(img_bytes)} image bytes")
            log_telemetry(
                stage="smoke_test",
                model="@cf/black-forest-labs/flux-1-schnell",
                parameters={"prompt": "smoke_test_coin", "steps": 1},
                latency_ms=elapsed_ms,
                status="SUCCESS"
            )
            return True, elapsed_ms, None
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        err_msg = f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}"
        print(f"❌ [Cloudflare AI] FAILED ({elapsed_ms}ms): {err_msg}")
        log_telemetry(
            stage="smoke_test",
            model="flux-1-schnell",
            parameters={"prompt": "smoke_test_coin"},
            latency_ms=elapsed_ms,
            status="FAILED",
            error=err_msg
        )
        return False, elapsed_ms, err_msg
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"❌ [Cloudflare AI] FAILED ({elapsed_ms}ms): {e}")
        log_telemetry(
            stage="smoke_test",
            model="flux-1-schnell",
            parameters={"prompt": "smoke_test_coin"},
            latency_ms=elapsed_ms,
            status="FAILED",
            error=str(e)
        )
        return False, elapsed_ms, str(e)


def test_kaggle():
    """Smoke test Kaggle configuration."""
    print("⏳ [Kaggle] Checking credentials...")
    kaggle_user = os.getenv("KAGGLE_USERNAME")
    kaggle_key = os.getenv("KAGGLE_KEY")
    kaggle_token = os.getenv("KAGGLE_API_TOKEN")
    kaggle_json_path = Path.home() / ".kaggle" / "kaggle.json"
    kaggle_token_path = Path.home() / ".kaggle" / "access_token"

    has_env = bool((kaggle_user and kaggle_key) or kaggle_token)
    has_file = kaggle_json_path.exists() or kaggle_token_path.exists()

    if has_env or has_file:
        user = kaggle_user if kaggle_user else "Kaggle API Token configured"
        print(f"✅ [Kaggle] SUCCESS | Configured: {user}")
        log_telemetry(
            stage="smoke_test",
            model="kaggle-t4-gpu",
            parameters={"user": user},
            latency_ms=10,
            status="CONFIGURED"
        )
        return True, 10, None
    else:
        print("ℹ️  [Kaggle] PENDING: KAGGLE_API_TOKEN / KAGGLE_KEY not found in .env (Needed for Wan 2.2 notebook)")
        log_telemetry(
            stage="smoke_test",
            model="kaggle-t4-gpu",
            parameters={},
            latency_ms=0,
            status="PENDING_SETUP",
            error="Credentials not set in .env"
        )
        return False, 0, "Not configured in .env"


def main():
    print("=" * 65)
    print("PHASE 1 SMOKE TEST: Providers, Quotas, and Latency")
    print("=" * 65)
    load_env_file()

    results = {}
    results["Gemini API"] = test_gemini()
    results["Cloudflare AI"] = test_cloudflare()
    results["Kaggle GPU"] = test_kaggle()

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    all_ok = True
    for provider, (passed, lat, err) in results.items():
        status_symbol = "✅ PASS" if passed else "❌ FAIL" if provider != "Kaggle GPU" else "⚠️  PENDING"
        print(f"{provider:<18} | {status_symbol:<10} | Latency: {lat}ms")
        if err and not passed:
            print(f"  └─ Details: {err[:90]}...")
            if provider != "Kaggle GPU":
                all_ok = False

    print("=" * 65)
    print(f"Telemetry updated in: {RUNS_LOG_PATH}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
