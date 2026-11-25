# ARCHITECTURE.md: Studio Pipeline Architecture & Contracts

This document specifies the technical architecture, data contracts, state management, caching algebra, and failure-handling strategies for **AI-Content-Generation: The Heritage Short**.

---

## 1. System Philosophy: The Single Contract Pattern

The architecture strictly adheres to the **Declarative Single Contract Pattern**. A single validated document—[`storyboard.json`](storyboard.json)—serves as the single source of truth for the entire pipeline.

No pipeline stage writes hidden state or communicates out-of-band with other stages. Every stage:
1. **Reads** its input parameters exclusively from `storyboard.json`.
2. **Generates** output artifacts to predictable, hash-addressed file paths in `outputs/`.
3. **Logs** execution telemetry (model, parameters, seed, latency, cost) to `runs.jsonl`.
4. **Writes** a lightweight atomic `.current` pointer recording the active file path.

```
                    ┌─────────────────────────┐
                    │     storyboard.json     │  ◄── Central Declarative Contract
                    │ (Validated with Schema) │
                    └───────────┬─────────────┘
                                │
        ┌──────────────┬────────┴────────┬──────────────┬──────────────┐
        ▼              ▼                 ▼              ▼              ▼
   [Validation]   [Narration]       [Keyframes]      [Music]        [Shots]
   `jsonschema`   Gemini TTS        FLUX.1 schnell  ACE-Step 1.5    Wan 2.2 /
   (Draft-07)       (`Puck`)         (Cloudflare)     (Synth)       Ken Burns
        │              │                 │              │              │
        │              ▼                 ▼              ▼              │
        │      radio_cut.wav       shot_01..08.jpg  selected_score     │
        │              │                 └──────────────┬──────────────┘
        │              │                                │
        │              │                                ▼
        │              │                         shot_01..08.mp4
        │              │                                │
        │              └────────────────┬───────────────┘
        │                               │
        │                               ▼
        │                         [Assembly]
        │                   FFmpeg Dual Export (9:16 & 16:9)
        │                   Ducking, -16 LUFS Loudnorm, Subs
        │                               │
        └───────────────────────────────┴──────────────────────────────┐
                                                                       ▼
                                                           ┌───────────────────────┐
                                                           │      runs.jsonl       │
                                                           │ (Real-Time Telemetry) │
                                                           └───────────────────────┘
```

---

## 2. Stage Contracts & Data Flow

Every stage enforces strict typing and schemas. Below are the precise data contracts governing each stage:

### 2.1 Validation Stage (`pipeline/validate.py`)
* **Contract Schema:** [`schema/storyboard.schema.json`](schema/storyboard.schema.json) (Draft-07 JSON Schema).
* **Guarantees:**
  - Validates overall duration (60–90 seconds target).
  - Enforces shot count (8–12 shots).
  - Validates presence of `visual_prompt`, `motion_prompt`, `narration.text`, and `music_cues`.
* **Exit Code:** `0` on validation success; non-zero halts pipeline immediately.

### 2.2 Narration Stage (`pipeline/narration.py`)
* **Input Contract:** `shots[i].narration.text`, `shots[i].narration.voice_style`.
* **Model:** Google Gemini Flash Audio (`gemini-2.5-flash-preview-tts`), Voice persona `Puck`.
* **Pacing & Breathing:** Generates per-shot 24kHz mono WAVs; stitches continuous master voiceover (`outputs/radio_cut_voiceover.wav`) with 250ms inter-shot breath intervals.
* **Output Contract:** `outputs/narration/{shot_id}_{hash}.wav` and `outputs/radio_cut_voiceover.wav`.

### 2.3 Keyframes Stage (`pipeline/keyframes.py`)
* **Input Contract:** `style_reference`, `shots[i].visual_prompt`, `shots[i].seed`.
* **Model:** `@cf/black-forest-labs/flux-1-schnell` via Cloudflare Workers AI.
* **Consistency Conditioning:** Generates global `character_reference.jpg` and `style_reference.jpg` first. Every shot prompt explicitly appends character details (10-year-old highland boy in cotton vest) and style block (cinematic 35mm, warm dawn lighting).
* **Output Contract:** `outputs/keyframes/{shot_id}_{hash}.jpg` (1024×1024, JPEG).

### 2.4 Moving Shots Stage (`pipeline/shots.py`)
* **Input Contract:** Keyframe image path + `shots[i].motion_prompt` + narration audio duration.
* **Engine:** Wan 2.2 TI2V-5B (Kaggle GPU) with cinematic FFmpeg Ken Burns motion engine.
* **Dynamic Audio-Video Sync:** Instead of arbitrary fixed durations, the engine probes the narration audio duration for that shot and renders video at $\text{Duration} = \text{AudioDuration} + 0.3\text{s}$, ensuring speech is never cut off.
* **Output Contract:** `outputs/shots/{shot_id}_{hash}.mp4` (1080p, 25fps H.264).

### 2.5 Music Stage (`pipeline/music.py`)
* **Input Contract:** `music_cues.caption`, `tempo_bpm`, `target_duration_sec`.
* **Engine:** ACE-Step 1.5 Ethio-acoustic physical modeling synthesizer.
* **Auditioning:** Synthesizes 3 distinct candidates (Tizita Minor 68 BPM, Bati Major 74 BPM, Anchihoye 62 BPM). Selects Candidate 1 into `selected_score.mp3` with full audition notes.
* **Output Contract:** `outputs/music/selected_score.mp3` (44.1kHz stereo, 88.0s).

### 2.6 Assembly Stage (`pipeline/assemble.py`)
* **Input Contract:** Ordered video clips + narration master + selected score + subtitle captions.
* **Engine:** Standalone FFmpeg 7.1 Filtergraph.
* **Features:**
  1. *Subtitles:* Programmatically generates and burns `.ass` subtitles with custom safe-area offsets (65px for 16:9; 380px for 9:16 mobile feeds).
  2. *Denoising:* Vocal FFT filtering (`afftdn=nf=-25`) removes floor hiss.
  3. *Ducking:* `sidechaincompress=threshold=0.015:ratio=8:attack=250:release=1200` lowers underscore under narration by -18 dB.
  4. *Loudnorm:* Normalizes audio to broadcast standard `-16 LUFS` (True Peak `-1.5 dBFS`).
  5. *Attribution:* Appends 3-second "Created with AI" end card.
* **Output Contract:**
  - `outputs/final/short_horizontal_16_9.mp4` (1920×1080)
  - `outputs/final/short_vertical_9_16.mp4` (1080×1920)

---

## 3. Caching Mathematics & Incremental Builds

To avoid wasteful re-computation and expensive GPU/API quota burn, every asset is addressed by a deterministic SHA-256 hash:

$$\text{CacheKey} = \text{SHA256}\Big(\text{shot\_id} \mathbin{\Vert} \text{prompt} \mathbin{\Vert} \text{duration} \mathbin{\Vert} \text{seed}\Big)[:16]$$

### Invalidation & Isolation Matrix

| What You Change in `storyboard.json` | What Regenerates | What Hits Cache (0 ms) |
| :--- | :--- | :--- |
| **Visual prompt of Shot 4** | Keyframe 4, Video Shot 4, Final Assembly | Shots 1–3 & 5–8, all Narration, Music Score |
| **Narration text of Shot 2** | Narration 2, Video Shot 2 (resync), Final Assembly | All Keyframes, Shots 1 & 3–8, Music Score |
| **Music tempo or cue** | Music Score, Final Assembly | All Keyframes, all Video Shots, all Narration |
| **Nothing (Clean Re-run)** | None | **100% Cache Hits** (Runs in ~12 seconds) |

---

## 4. Failure Handling, Circuit Breakers & Fallbacks

The studio pipeline incorporates multi-layered fault tolerance:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Resilience Mechanisms                           │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Failure Scenario             │ Autonomous Resolution Mechanism         │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Cloud API Rate Limit (429)   │ Exponential backoff retry loop          │
│                              │ (4s, 8s, 16s) with cached shot skipping │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Kaggle GPU Timeout / Quota   │ Smooth fallback to cinematic Ken Burns  │
│                              │ pan/tilt/push-in video generator        │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Missing System FFmpeg Binary │ Automatic discovery fallback to bundled │
│                              │ `imageio-ffmpeg` Apple Silicon binary   │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Cloudflare Payload Schema    │ Automatic schema sanitization stripping │
│ Validation Error (400)       │ unsupported custom seed parameters      │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Background Audio Noise       │ FFT spectral denoising (`afftdn`) and   │
│                              │ steep low-pass filtering on underscore  │
└──────────────────────────────┴─────────────────────────────────────────┘
```

---

## 5. Telemetry Architecture (`runs.jsonl`)

Every external call, generation, and compilation is recorded as a single JSON line in [`runs.jsonl`](runs.jsonl):

```json
{
  "timestamp": "2026-11-25T18:25:26.120Z",
  "stage": "final_assembly",
  "shot_id": "dual_export_master",
  "model": "ffmpeg-dual-export",
  "parameters": {
    "horizontal": "short_horizontal_16_9.mp4",
    "vertical": "short_vertical_9_16.mp4",
    "loudnorm": "-16 LUFS",
    "ducking": "sidechaincompress",
    "subtitles": "burned"
  },
  "seed": 42,
  "latency_ms": 27129,
  "cost_usd": 0.0
}
```

This guarantees 100% auditability and verifiable proof of model calls for academic and technical review.
