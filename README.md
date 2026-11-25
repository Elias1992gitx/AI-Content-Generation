# AI-Content-Generation: The Heritage Short

> An automated, code-driven studio pipeline that transforms a validated `storyboard.json` into a 60–90 second short film with native narration, original score ducking, and dual-aspect exports (9:16 vertical and 16:9 horizontal).

---

## ⚡ Quick Start (One-Command Run)

### 1. Prerequisites
* Python 3.10+
* `ffmpeg` installed on your machine (`brew install ffmpeg` on macOS)

### 2. Setup
```bash
# Clone the repository
git clone <repo_url> AI-Content-Generation
cd AI-Content-Generation

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment variables template
cp .env.example .env
```

### 3. Run the Pipeline
To validate the contract and generate the short film end-to-end:
```bash
python run_pipeline.py
```

To force-regenerate all assets ignoring cache:
```bash
python run_pipeline.py --force
```

To run a single stage (e.g., narration or keyframes):
```bash
python run_pipeline.py --stage narration
```

---

## 📁 Repository Structure

```text
├── README.md                  # This one-command run & project overview
├── storyboard.json            # Central contract: shots, durations, prompts, narration, audio cues
├── schema/
│   └── storyboard.schema.json # JSON Schema validating storyboard.json
├── pipeline/                  # Modular stage scripts
│   ├── common.py              # SHA-256 hash caching and runs.jsonl logging helper
│   ├── validate.py            # Validates storyboard.json against schema
│   ├── script.py              # Scripting and prompt refinement
│   ├── narration.py           # Gemini 3.8 Flash TTS per shot
│   ├── keyframes.py           # FLUX.1 schnell via Cloudflare Workers AI
│   ├── shots.py               # Wan 2.2 I2V with FFmpeg Ken Burns fallback
│   ├── music.py               # ACE-Step 1.5 score generator
│   └── assemble.py            # FFmpeg audio ducking, subtitles, and dual export
├── run_pipeline.py            # Master CLI runner
├── runs.jsonl                 # Telemetry log: model, seed, parameters, latency, cost
├── outputs/                   # Generated artifacts per stage
│   ├── keyframes/
│   ├── shots/
│   ├── narration/
│   ├── music/
│   └── final/                 # Final 9:16 vertical & 16:9 horizontal MP4 exports
├── DESIGN.md                  # Audience intent, shot reasons, and 2 user test logs
├── ARCHITECTURE.md            # Pipeline DAG, stage contracts, caching, and recovery
├── EXPERIMENTS.md             # 10+ hypothesis -> change -> result entries
├── FAILURES.md                # Real blockers encountered and how they were solved
├── COSTS.md                   # Latency, GPU minutes, and commercial cost comparisons
└── ETHICS.md                  # Likeness consent record, model licenses, and AI disclosures
```

---

## 🏗️ Architecture & Caching

The pipeline operates around a single contract: `storyboard.json`.
Every stage generates a deterministic SHA-256 hash of its inputs:
$$\text{CacheKey} = \text{SHA256}(\text{shot\_id} + \text{prompt} + \text{parameters} + \text{seed})[:16]$$

* **Granular Re-runs:** Modifying Shot 3 only re-runs Shot 3. The other 7 shots are retrieved from cache in $< 100\text{ ms}$.
* **Telemetry:** Every model call automatically appends an entry to `runs.jsonl`.
* **Zero Cost:** Uses Gemini free tier, Cloudflare Workers AI free allowance, and open-weight models with zero credit card requirements.
