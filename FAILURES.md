# FAILURES.md: Real Blocker & Resolution Post-Mortem

Authentic log of technical issues encountered during pipeline development, what was tried, and how each was resolved.

### Failure 1: HTTP 429 Rate Limiting on Gemini Flash TTS
* **Symptom:** During sequential narration generation, Shot 5 and Shot 6 failed with `urllib.error.HTTPError: HTTP Error 429: Too Many Requests`.
* **Root Cause:** The Google AI Studio free tier enforces a requests-per-minute (RPM) threshold for preview audio modalities. Firing 8 consecutive audio generation requests without a cooldown tripped the burst rate limiter.
* **What We Tried:**
  1. *Immediate retry without delay:* Failed with the same 429 status code.
  2. *Relied on granular caching & backoff:* Leveraged SHA-256 caching so that Shots 1–4 and 7–8 were recognized as cache hits (`0ms` latency), and added an exponential backoff retry loop (starting at 4 seconds, doubling per attempt).
* **Resolution:** Re-running the pipeline hit the cache for previously generated shots and smoothly retried Shots 5 and 6, generating all 8 audio files with zero dropped frames.

---

### Failure 2: System Python Dependency Isolation
* **Symptom:** Running submodules directly (`python3 pipeline/narration.py`) threw `ImportError: attempted relative import with no known parent package`.
* **Root Cause:** Executing scripts directly as top-level modules breaks Python's relative import syntax (`from .common import ...`).
* **What We Tried:**
  1. Forcing execution only via module flag (`python3 -m pipeline.narration`).
  2. Adding try/except fallback imports in each script (`try: from .common ... except ImportError: from common ...`).
* **Resolution:** Implemented import fallback handling across all pipeline scripts so developers can execute stages either via the master CLI (`python3 run_pipeline.py --stage narration`), as modules (`python3 -m pipeline.narration`), or directly.

---

### Failure 3: Cloudflare Workers AI FLUX.1 Schema Validation (HTTP 400)
* **Symptom:** FLUX.1 schnell API call returned `HTTP Error 400: Bad Request` when passing explicit numeric seeds.
* **Root Cause:** Cloudflare Workers AI FLUX endpoint rejected custom integer seeds beyond its supported parameter schema for `@cf/black-forest-labs/flux-1-schnell`.
* **What We Tried:**
  1. Passing seeds within 0–10000 range.
  2. Conforming request payload strictly to `{"prompt": prompt, "steps": 4}`.
* **Resolution:** Stripped unsupported seed arguments from the Cloudflare payload; API responded with HTTP 200 OK and generated high-resolution 1024x1024 JPEG keyframes.

---

### Failure 4: FFmpeg Binary Missing on System PATH
* **Symptom:** Video shot rendering and audio conversion failed with `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`.
* **Root Cause:** The host macOS environment lacked a globally installed `ffmpeg` binary or Homebrew package manager.
* **What We Tried:**
  1. Checking `/usr/local/bin` and `/opt/homebrew/bin` (both missing).
  2. Installing `imageio-ffmpeg` via Python user site-packages.
* **Resolution:** Created `get_ffmpeg_cmd()` in `pipeline/common.py` that discovers the precompiled Apple Silicon FFmpeg 7.1 binary at `/Users/mac/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1`, providing full H.264, AAC, and filter graph support without root permissions.

---

### Failure 5: Kaggle CLI Token Authentication Format Mismatch
* **Symptom:** Running `kaggle` CLI threw `OSError: Could not find kaggle.json. Make sure it's located in /Users/mac/.kaggle`.
* **Root Cause:** Kaggle's website generated a single `KAGGLE_API_TOKEN` string (`KGAT_...`), whereas the python `kaggle` package defaults to reading `kaggle.json` containing `{"username": "...", "key": "..."}` or `KAGGLE_USERNAME`/`KAGGLE_KEY` environment variables.
* **What We Tried:**
  1. Setting only `export KAGGLE_API_TOKEN=...` in terminal (ignored by CLI 1.7.4).
  2. Creating `~/.kaggle/kaggle.json` with the username `eliaschane` and key `KGAT_...` and setting matching env variables.
* **Resolution:** Formatted credentials in both `~/.kaggle/kaggle.json` and `.env`; verified authentication via `kaggle datasets list -m` returning HTTP 200 OK.
