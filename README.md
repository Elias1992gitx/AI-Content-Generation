# AI-Content-Generation: The Heritage Short

> **"The Boy Who Grew with the Land" (ከመሬቱ ጋር ያደገው ልጅ)**  
> An autonomous, code-driven film studio pipeline that transforms a single validated contract (`storyboard.json`) into a polished 86-second short film featuring authentic Amharic narration, original Ethio-acoustic score ducking, English subtitles, and dual exports (9:16 vertical and 16:9 horizontal).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![FFmpeg 7.1](https://img.shields.io/badge/FFmpeg-7.1-orange.svg)](https://ffmpeg.org/)
[![Zero-Cost Stack](https://img.shields.io/badge/Cost-%240.00%20(Free%20Tier)-success.svg)](COSTS.md)

---

## ⚡ Quick Start: One-Command Reproduction

The entire studio pipeline runs from a clean clone with a single command:

```bash
# 1. Clone repository
git clone https://github.com/eliaschane/AI-Content-Generation.git
cd AI-Content-Generation

# 2. Install dependencies (includes standalone FFmpeg 7.1)
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Fill in GEMINI_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, and KAGGLE credentials

# 4. Run the entire film studio pipeline
make film
```
*(Alternatively, run `python3 run_pipeline.py` directly).*

---

## 📽️ Film Synopsis & Thematic Intent

* **Title:** The Boy Who Grew with the Land
* **Protagonist:** A 10-year-old boy in rural Ethiopian highlands herding cattle, preparing soil, and cultivating seeds.
* **Core Message:** *"Some people inherit wealth, some inherit knowledge, but my father inherited the strength of the land — and that is a legacy to be proud of."*
* **Narrative Language:** Amharic (`am-ET`) with calibrated storytelling cadence and burned English subtitles.
* **Exports Produced:**
  1. **Mobile Vertical (9:16):** [`outputs/final/short_vertical_9_16.mp4`](outputs/final/short_vertical_9_16.mp4) (1080×1920, 86.3s, 24.9 MB)
  2. **Cinematic Horizontal (16:9):** [`outputs/final/short_horizontal_16_9.mp4`](outputs/final/short_horizontal_16_9.mp4) (1920×1080, 86.3s, 28.4 MB)

---

## 🏗️ Studio Architecture & Stage Boundaries

The entire production is decoupled into 5 deterministic stages governed by the machine-readable contract [`storyboard.json`](storyboard.json), strictly validated against [`schema/storyboard.schema.json`](schema/storyboard.schema.json):

```
                   ┌──────────────────────────────┐
                   │       storyboard.json        │  ◄── Single Source of Truth
                   │   (Validated with Schema)    │
                   └──────────────┬───────────────┘
                                  │
         ┌──────────────┬─────────┼──────────────┬──────────────┐
         ▼              ▼         ▼              ▼              ▼
    [keyframes]      [shots]   [narration]    [music]       [assemble]
   FLUX.1 schnell    Wan 2.2   Gemini Flash  ACE-Step 1.5   FFmpeg Dual
   Cloudflare AI    Ken Burns      TTS        Acoustic      Export + Subs
         │              │         │              │              │
         └──────────────┴─────────┼──────────────┴──────────────┘
                                  │
                   ┌──────────────▼───────────────┐
                   │          runs.jsonl          │  ◄── Structured Telemetry
                   └──────────────────────────────┘
```

### Stage Summary

| Stage | Script | Engine / Model | Execution Target | Output Asset |
| :--- | :--- | :--- | :--- | :--- |
| **0. Validation** | `pipeline/validate.py` | `jsonschema` (Draft-07) | Local CPU | Contract validation exit 0 |
| **1. Narration** | `pipeline/narration.py` | Gemini Flash TTS (`Puck`) | Google AI Studio | `outputs/radio_cut_voiceover.wav` (83.3s) |
| **2. Keyframes** | `pipeline/keyframes.py` | FLUX.1 schnell (Conditioned) | Cloudflare Workers AI | `outputs/keyframes/shot_01..08.jpg` |
| **3. Video Shots** | `pipeline/shots.py` | Ken Burns Motion / Wan 2.2 | Local H.264 / Kaggle GPU | `outputs/shots/shot_01..08.mp4` (84.2s) |
| **4. Music Score** | `pipeline/music.py` | ACE-Step 1.5 Physical Synth | Local Audio / Kaggle | `outputs/music/selected_score.mp3` (88.0s) |
| **5. Assembly** | `pipeline/assemble.py` | FFmpeg 7.1 Filtergraph | Local CPU / Media Engine | Dual 9:16 & 16:9 Final Masters |

---

## ⚡ Granular SHA-256 Caching & Live Regeneration

Every stage computes a deterministic hash of its exact inputs:
$$\text{CacheKey} = \text{SHA256}(\text{shot\_id} + \text{prompt} + \text{duration} + \text{seed})[:16]$$

* **Zero-Waste Re-runs:** Unchanged shots are recognized in 0 ms.
* **1-Shot Live Demo:** If you modify Shot 4 in `storyboard.json` and re-run `make film`, shots 1–3 and 5–8 hit the cache instantly, regenerating **only** the modified shot in under 3 seconds.

---

## 🎚️ Audio Engineering: Ducking, Loudnorm & Denoising

1. **Sidechain Ducking (`sidechaincompress`):** Music automatically ducks by -18 dB when the narrator speaks and swells gently during pauses (`threshold=0.015`, `ratio=8`, `attack=250ms`, `release=1200ms`).
2. **Loudness Normalization (`loudnorm`):** Master audio is normalized to EBU R128 standard: **-16 LUFS**, True Peak **-1.5 dBFS**.
3. **Spectral Denoising (`afftdn`):** High-pass filtering at 75 Hz and FFT noise suppression strip background room hiss, leaving dialogue pristine.

---

## 💰 Cost Accounting Summary

Every external API call and compute resource is tracked in [`runs.jsonl`](runs.jsonl) and summarized in [`COSTS.md`](COSTS.md):

* **Total Actual Cost:** **$0.00** (Runs entirely on free tiers).
* **Commercial Equivalent Cost:** ~$5.25 per full production run (ElevenLabs + Midjourney + Runway Gen-3 + Suno).
* **Wall-Clock Latency:**
  - *Cold Run (all assets generated from scratch):* ~192 seconds.
  - *Cached Re-run (full end-to-end pass):* **12.7 seconds**.

---

## 📁 Repository Directory Map

```text
├── Makefile                   # make film, make validate, make narration, etc.
├── README.md                  # Comprehensive studio overview & execution guide
├── ARCHITECTURE.md            # Stage contracts, DAG, caching mathematics, and recovery
├── DESIGN.md                  # Audience intent, shot rationales, and User Tests 1 & 2
├── EXPERIMENTS.md             # 11 hypothesis → change → result structured entries
├── FAILURES.md                # Authentic post-mortems of real technical blockers
├── COSTS.md                   # Latency benchmarks, GPU minutes, and commercial cost accounting
├── ETHICS.md                  # Likeness consent, open-weights licensing, and AI disclosures
├── storyboard.json            # Central declarative contract (8 shots, prompts, audio cues)
├── runs.jsonl                 # Telemetry log per model invocation
├── requirements.txt           # Project dependencies including imageio-ffmpeg
├── run_pipeline.py            # Master CLI runner with stage filtering
├── schema/
│   └── storyboard.schema.json # JSON Schema for storyboard validation
├── pipeline/
│   ├── common.py              # Hash caching, runs.jsonl logger, FFmpeg discovery
│   ├── validate.py            # Storyboard validation script
│   ├── narration.py           # Gemini Flash TTS voiceover engine
│   ├── keyframes.py           # FLUX.1 schnell keyframe generation
│   ├── shots.py               # Cinematic video shots generation
│   ├── music.py               # ACE-Step 1.5 Ethiopian score candidate synthesizer
│   └── assemble.py            # Dual-export master assembly & subtitle burning
├── kaggle/
│   ├── wan2_ti2v_kaggle.py    # Wan 2.2 TI2V-5B script for Kaggle GPU (T4)
│   └── kernel-metadata.json   # Kaggle CLI kernel configuration
└── outputs/
    ├── keyframes/             # Character & style anchors + 8 keyframe stills
    ├── shots/                 # 8 rendered video clips
    ├── narration/             # Per-shot narration WAVs + master radio cut
    ├── music/                 # 3 audition candidates + selected Tizita score
    └── final/                 # short_vertical_9_16.mp4 & short_horizontal_16_9.mp4
```

---

## ⚖️ Ethics, Licensing & Attribution

* **Consent:** Full informed consent for depicting family childhood memories is documented in [`ETHICS.md`](ETHICS.md).
* **Licenses:**
  - FLUX.1 schnell: Apache 2.0
  - Wan 2.2: Apache 2.0
  - ACE-Step 1.5: MIT License
* **Attribution:** Both final exports include a visible 3-second end card:  
  *"THE BOY WHO GREW WITH THE LAND • A tribute to Ethiopian farming heritage • Created with AI • Antigravity Studio"*.
