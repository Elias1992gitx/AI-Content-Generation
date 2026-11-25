# Project Implementation Action Plan: AI-Content-Generation

> **Project Name:** AI-Content-Generation (The Heritage Short)  
> **Course / Track:** B2W0: AI-Content Generation  
> **Target Deadline:** Thursday, 26 November 2026 at 23:59 East Africa Time (EAT)  
> **Core Objective:** Build a reproducible, code-driven studio pipeline that transforms a validated `storyboard.json` contract into a 60–90 second dual-aspect short film (9:16 vertical & 16:9 horizontal) with native-language narration, ducked original score, and burned English subtitles.

---

## 1. Architectural Principles & Evaluation Rules

1. **Contract-Driven Design:** `storyboard.json` is the sole source of truth between all 5 stages (`keyframes`, `shots`, `narration`, `music`, `assemble`).
2. **Granular Invalidation & Smart Caching:** Changing 1 shot in `storyboard.json` must **only** regenerate that specific shot; cached shots remain untouched.
3. **Structured Telemetry (`runs.jsonl`):** Every single model call must log `timestamp`, `stage`, `model_name`, `parameters`, `seed`, `latency_ms`, and `cost_usd`.
4. **Zero Secrets in Code:** Credentials and API keys belong strictly in `.env` or environment variables.
5. **Zero-Tolerance Ethical Gate:** If any real person's likeness or voice is depicted, explicit informed consent **must** be recorded in `ETHICS.md` before generating media.
6. **One-Command Reproducibility:** A clean clone must run end-to-end via a single command (e.g., `python run_pipeline.py` or `make film`).

---

## 2. Zero-Cost Tech Stack & Compute Strategy

| Pipeline Stage | Model / Tool | Execution Environment | Quotas & Strategy |
| :--- | :--- | :--- | :--- |
| **Orchestration & Coding** | Antigravity CLI (`agy`) / OpenCode | Local Terminal | Automated stage scripting |
| **Schema Validation** | `jsonschema` (Python) | Local CPU | Validates contract before any stage runs |
| **Script & Storyboard** | Gemini 3.8 Flash / Flash-Lite | Google AI Studio API | Free tier (Ethiopia supported) |
| **Narration (TTS)** | Gemini 3.8 Flash TTS | Google AI Studio API | Multilingual (Amharic), shot-by-shot generation |
| **Keyframes (Images)** | FLUX.1 schnell / FLUX.2 klein | Cloudflare Workers AI | Daily free allowance (~50–170 images) |
| **Moving Shots (Video)** | Wan 2.2 TI2V-5B *(or HunyuanVideo 1.5)* | Kaggle Notebooks (2× T4 GPUs) | Batch runs; **Fallback: FFmpeg Ken Burns pan/zoom** |
| **Original Music** | ACE-Step 1.5 | Kaggle or Colab | Audition 3 candidates; MIT license |
| **Assembly & Mixing** | FFmpeg | Local Machine | `sidechaincompress` ducking, `loudnorm` to -14 LUFS |

---

## 3. Phased Implementation Timeline

```
                                  TIMELINE OVERVIEW
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE 1: Scaffolding, Schema & Telemetry Engine (Hours 0 – 3)                     │
│ MILESTONE 2: Story Definition, Radio Cut & User Test 1 (Hours 3 – 8)                  │
│ MILESTONE 3: Asset Generation: Keyframes, Video & Music (Hours 8 – 18)                │
│ MILESTONE 4: Programmatic Assembly, Polish & User Test 2 (Hours 18 – 26)              │
│ MILESTONE 5: Walkthrough Video, Documentation & Final Submission (Hours 26 – 34)      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Milestone 1: Scaffolding, Schema & Telemetry Engine (Day 1: Morning)

- [ ] **Repository Directory Layout:**
  ```text
  ├── README.md                  # One-command execution guide & cost summary
  ├── ACTION_PLAN.md             # This implementation action plan
  ├── storyboard.json            # Central contract for all shots
  ├── schema/
  │   └── storyboard.schema.json # JSON Schema for storyboard.json
  ├── pipeline/
  │   ├── __init__.py
  │   ├── common.py              # Hash-based caching, runs.jsonl logging helper
  │   ├── validate.py            # Validates storyboard.json against schema
  │   ├── narration.py           # Gemini Flash TTS per shot
  │   ├── keyframes.py           # Cloudflare Workers AI FLUX.1 caller
  │   ├── shots.py               # Wan 2.2 bridge + Ken Burns fallback
  │   ├── music.py               # ACE-Step 1.5 score generator/selector
  │   └── assemble.py            # FFmpeg audio ducking, subtitle burn, dual export
  ├── run_pipeline.py            # Master CLI runner
  ├── runs.jsonl                 # Telemetry log
  ├── outputs/
  │   ├── keyframes/
  │   ├── shots/
  │   ├── narration/
  │   ├── music/
  │   └── final/
  ├── DESIGN.md                  # Audience intent & 2 user testing logs
  ├── ARCHITECTURE.md            # DAG flow, caching, contracts, failure recovery
  ├── EXPERIMENTS.md             # 10+ hypothesis -> change -> result entries
  ├── FAILURES.md                # Real errors, root causes, and solutions
  ├── COSTS.md                   # Latency, GPU minutes, list-price equivalent
  └── ETHICS.md                  # Consent record, licenses, AI disclosure
  ```
- [ ] **Build `pipeline/common.py`:**
  - Compute SHA-256 cache key from `(shot_id, prompt, seed, parameters)`.
  - Check if target output exists; if yes, log cache hit and bypass API call.
  - Append every real call to `runs.jsonl`:
    ```json
    {"timestamp": "ISO8601", "stage": "narration", "shot_id": "shot_01", "model": "gemini-3.8-flash-tts", "seed": 42, "latency_ms": 1150, "cost_usd": 0.0}
    ```
- [ ] **Define `schema/storyboard.schema.json`:**
  - Validate shot list (8–12 shots), `duration_sec`, `visual_prompt`, `camera_motion`, `voiceover_text`, `audio_cue`, `seed`.

---

### Milestone 2: Story, Radio Cut & User Test 1 (Day 1: Midday to Evening)

- [ ] **Story Choice & Ethics:**
  - Select family/cultural narrative (e.g. grandmother's market walk, radio repair, mother's proverb).
  - Draft consent documentation in `ETHICS.md` (mandatory).
  - Define audience and desired emotional resonance in `DESIGN.md`.
- [ ] **Draft `storyboard.json`:**
  - 8 to 12 shots totaling 60–90 seconds.
  - Script narration (~130–180 words in native language, e.g. Amharic).
- [ ] **Generate Narration & Radio Cut:**
  - Run `python -m pipeline.narration` to generate individual audio files for each shot.
  - Combine narration tracks with temporary placeholder music over black frames.
- [ ] **Execute User Test 1 (Checkpoint 1):**
  - Screen the radio cut to at least 3 people from your target audience.
  - Record feedback in `DESIGN.md` (pacing, clarity, tone).
  - Document at least 2 specific adjustments made to `storyboard.json` based on feedback.

---

### Milestone 3: Asset Generation & Compute Management (Day 1 Evening to Day 2 Afternoon)

- [ ] **Visual Anchor & Keyframes:**
  - Generate a **Character & Style Reference Sheet** first to lock facial features and aesthetic.
  - Generate keyframe stills for each shot using FLUX.1 schnell on Cloudflare Workers AI.
  - Ensure centered subject composition to accommodate both 9:16 and 16:9 crops.
- [ ] **Video Generation (Wan 2.2 on Kaggle / Fallback):**
  - Execute image-to-video for key shots via Kaggle notebook (2× T4 GPUs).
  - Use motion-only and camera-only prompts (do not re-describe the static scene).
  - **The Circuit Breaker:** If Kaggle queues exceed quota limits or render fails after 2 attempts, trigger the FFmpeg Ken Burns pan/zoom generator.
- [ ] **Music Generation (ACE-Step 1.5):**
  - Generate 3 score candidates with distinct tempo/mood captions.
  - Select the winning track and record reasoning in `EXPERIMENTS.md`.
- [ ] **Document Progress:**
  - Add at least 5 entries to `EXPERIMENTS.md` (testing prompts, seeds, motion parameters).
  - Record any GPU OOM, API timeout, or prompt degradation in `FAILURES.md`.

---

### Milestone 4: Programmatic Assembly & Dual-Aspect Export (Day 2: Afternoon to Evening)

- [ ] **FFmpeg Assembly Engine (`pipeline/assemble.py`):**
  - **Audio Ducking:** Apply `sidechaincompress` (`threshold=0.02:ratio=6:attack=300:release=1500`) so music lowers under narration.
  - **Loudness Normalization:** Apply `loudnorm` filter targeting `-14 LUFS` and true peak `-1 dBFS`.
  - **Subtitles:** Generate and burn English subtitles formatted in safe areas ($\le 40$ chars/line).
  - **End Card:** Append a 3-second explicit "Created with AI" disclosure card.
  - **Dual Export:** Render both `outputs/final/short_vertical_9_16.mp4` and `outputs/final/short_horizontal_16_9.mp4`.
- [ ] **Execute User Test 2 (Checkpoint 2):**
  - Screen the near-final cut to 3+ audience members.
  - Log responses in `DESIGN.md` and make final timing/audio balance adjustments.

---

### Milestone 5: Documentation, Walkthrough Video & Submission (Day 2: Evening to 23:59 EAT)

- [ ] **Finalize Documentation:**
  - `README.md`: Step-by-step setup, prerequisites, and one-command execution (`python run_pipeline.py`).
  - `ARCHITECTURE.md`: Pipeline stage contracts, caching hash scheme, fallback mechanics.
  - `EXPERIMENTS.md`: Complete $\ge 10$ hypothesis $\to$ change $\to$ result entries.
  - `FAILURES.md`: Comprehensive breakdown of failures, debugging steps, and final fixes.
  - `COSTS.md`: Measured runtimes, latency percentiles, GPU minutes, and list-price equivalents.
  - `ETHICS.md`: Signed consent entries, license registry (Apache 2.0, MIT), disclosure statement.
- [ ] **Record the 5-Minute Walkthrough Video:**
  - Explain pipeline architecture and contracts (1.5 min).
  - Discuss one challenging engineering trade-off or failure (1.5 min).
  - **Live Caching Demo (2 min):** Modify one prompt in `storyboard.json`, execute pipeline, and show on screen via `runs.jsonl` that only that shot regenerated while others hit cache.
- [ ] **Publish Public Post:**
  - Share on LinkedIn / X / social media with AI content label enabled; capture link/screenshot.
- [ ] **Write Report:**
  - Prepare written report addressing design intent, user test learnings, instinct-vs-practice reflection, and ceiling work.
- [ ] **Final Submission (before 23:59 EAT):**
  - **Assignment 1:** GitHub repository URL + Report document.
  - **Assignment 2:** Vertical 9:16 MP4 link, Horizontal 16:9 MP4 link, Walkthrough video link, Public post link/screenshot.
  - **AI Interview Prep:** Review logs and notes to speak confidently on architectural choices.

---

## 4. Grading Rubric Quick Reference

| Deliverable | Points | Critical Success Factors |
| :--- | :---: | :--- |
| **Software Eng & Reproducibility** | 20 | Single run command, strict caching, schema validation, zero committed secrets. |
| **Documentation & Architecture** | 10 | Clear `README.md` and `ARCHITECTURE.md` explaining contracts and retries. |
| **Design Thinking & Audience** | 10 | Documented User Test 1 & 2 ($\ge 3$ people each); visible storyboard changes. |
| **Experimentation & Failures** | 20 | $\ge 10$ hypothesis-driven experiments; authentic failure post-mortems in `FAILURES.md`. |
| **Measurement & Ethics** | 10 | Latency/cost breakdown in `COSTS.md`; recorded subject consent in `ETHICS.md`. |
| **Written Report Reflections** | 30 | Deep reflection on audience feedback, practices tested, and ceiling work. |
| **The Film (Assignment 2)** | 50 | 60–90s, dual formats, ducked score, clear narration, English subtitles, AI end card. |
| **Walkthrough Video** | 30 | Under 5 mins, clear architecture explanation, **live 1-shot cache demo**. |
| **Public Post** | 20 | Authored story with platform AI disclosure enabled. |
| **TOTAL** | **200** | *Note: Missing consent in ETHICS.md yields automatic zero on film.* |

