# AI-Content Generation: The Heritage Short
## Technical Engineering, Design Thinking & Reflection Report

**Project Title:** The Boy Who Grew with the Land (ከመሬቱ ጋር ያደገው ልጅ)  
**Author:** Elias Chane  
**Repository:** [github.com/eliaschane/AI-Content-Generation](https://github.com/eliaschane/AI-Content-Generation)  
**Date:** November 2026  
**Cohort:** TenX Bi-Weekly Challenge (B2W0)

---

## 1. Executive Summary & Intent

### 1.1 What We Set Out to Make
"The Boy Who Grew with the Land" is an 86-second cinematic short film documenting the childhood of my father in the Ethiopian highlands. Long before modern urban life, my father grew up in rural Ethiopia waking at dawn, herding cattle and sheep, cultivating the soil, and planting seeds. The film illustrates that character, patience, and dignity were forged not in modern classrooms, but through intimate responsibility to family and the land.

The central emotional thesis of the film is captured in its final narrative resolution:
> *"Some people inherit wealth, some inherit knowledge, but my father inherited the strength of the land — and that is a legacy to be proud of."*

### 1.2 Target Audience & Context
1. **Primary Audience:** Family members and elders who share and cherish this rural memory.
2. **Secondary Audience:** The Ethiopian diaspora and urban youth who are often disconnected from the agrarian roots and manual labor that built previous generations.
3. **Viewing Medium:** Designed natively for mobile consumption (9:16 vertical video for TikTok, Instagram Reels, and Telegram family groups) with an accompanying cinematic landscape master (16:9 for YouTube).

---

## 2. Audience Reflection & Testing Cycles

In accordance with human-centered design thinking, the film was developed through two iterative prototype feedback loops with three live audience members.

### 2.1 User Test 1: The Radio Cut (Narration & Pacing Prototype)
* **Prototype:** A black-screen animatic combining raw Gemini Flash TTS audio and placeholder music.
* **Audience Feedback:**
  - *Listener 1 (Family Member):* Observed that the vocal tone shifted abruptly between shots, sounding like two different speakers.
  - *Listener 2 (Relative):* Noticed that while the opening tone was warm, subsequent lines felt rushed and slightly artificial.
  - *Listener 3 (Native Speaker):* Urged making the storytelling transitions between herding cattle and farming seeds flow as a single continuous memory rather than disjointed sentences.
* **Evidence-Based Changes in Code:**
  1. *Voice Persona Locking:* Permanently locked the voice model to `Puck` across all 8 shots, eliminating speaker drift (`pipeline/narration.py`).
  2. *Breath Pauses:* Implemented an audio stitching engine that injects 250ms of natural breath silence between shots (`outputs/radio_cut_voiceover.wav`).
  3. *Script Refinement:* Rewrote Shot 4 narration to specifically highlight seed cultivation as an agrarian school of life.

### 2.2 User Test 2: Near-Final Cut (Visuals, Ducking & Subtitles)
* **Prototype:** Full mobile screening of `short_vertical_9_16.mp4` with moving video, burned subtitles, and background score.
* **Audience Feedback:**
  - *Viewer 1 (Elder):* "The imagery is touching, but there is an annoying buzzing noise in the background behind the voice."
  - *Viewer 2 (Content Creator):* "The subtitles in vertical format are great, but the background music is too loud during voice pauses."
  - *Viewer 3 (Cousin):* "Make the background sound smooth and peaceful like the countryside so his words remain intimate."
* **Evidence-Based Changes in Code:**
  1. *Score Noise Elimination:* Discovered that the physical modeling synthesizer was injecting randomized white noise to emulate reed breath. Completely removed the noise generator in `pipeline/music.py`, retaining only pure warm acoustic overtones.
  2. *Vocal Stem Denoising:* Added FFT spectral noise suppression (`afftdn=nf=-25`) and rumble roll-off (`highpass=f=75`) in `pipeline/assemble.py`.
  3. *Underscore Rebalancing:* Reduced music pre-gain from `0.35` to `0.10` (-20 dB true underscore), retuned sidechain ducking (`ratio=8`, `attack=250ms`, `release=1200ms`), and normalized to `-16 LUFS` (`TP=-1.5 dBFS`). Background noise was completely eliminated.

---

## 3. The Hardest Technical Challenge & Resolution

### The Challenge: Dynamic Audio-Visual Sync & Subtitle Safe-Areas
In generative media pipelines, video diffusion models typically output fixed-duration clips (e.g., exactly 5.0 seconds). However, natural human narration lines in Amharic fluctuate between 7.5 and 14.5 seconds depending on grammatical cadence. Early drafts suffered from two critical defects:
1. Video clips cut off prematurely before the narrator finished speaking.
2. Standard subtitle placement at the bottom of the frame was obstructed by mobile platform UI buttons (like, comment, and share icons).

### The Solution:
1. **Dynamic Audio-Video Sizing Engine:** Built a duration inspection mechanism in `pipeline/shots.py`. The video generator probes the exact duration of the generated narration WAV for each shot and dynamically computes the video duration as:
   $$\text{Duration}_{\text{video}} = \text{Duration}_{\text{audio}} + 0.30\text{s}$$
   This guarantees an exact synchronization between image motion and speech with a natural 300ms tail pad.
2. **Safe-Area Subtitle Geometry:** Rather than relying on simple center-cropping, `pipeline/assemble.py` compiles distinct `.ass` scripts for each aspect ratio. For vertical 9:16, subtitles are pinned with a bottom margin of **380 pixels** (`MarginV=380`), positioning the text in the platform-safe reading zone.

---

## 4. Suggested Practices Tested Honestly

### 4.1 The Practice That Beat My Instinct: "Timing Narration First (The Radio Cut)"
* **My Initial Instinct:** As a visual developer, my instinct was to immediately generate keyframes and video clips to see what the film would look like.
* **What Happened:** Forcing myself to assemble the radio cut first established an immutable temporal anchor. Because spoken Amharic dictates the narrative rhythm, knowing the exact shot lengths (e.g., Shot 4 needed 14.9s for seed cultivation reflection) prevented dozens of costly regenerations of video shots. Editing picture to voice saved GPU quota and produced a cohesive film structure.

### 4.2 The Practice That Did Not Beat My Instinct: "Relying on Generic Zero-Shot Video Prompts"
* **The Suggested Practice:** Relying solely on text-to-video prompts to establish action and identity.
* **What Happened:** When feeding descriptive prompts directly into video models without strict image conditioning, the boy's face, skin tone, and clothing drifted wildly between shots. My instinct to establish a strict **two-step reference anchor**—first generating `character_reference.jpg` and `style_reference.jpg` via FLUX.1, and conditioning every video clip directly on that keyframe still—drastically outperformed text-only prompting and achieved authentic character consistency.

---

## 5. Ceiling Work (Curiosity Beyond the Floor)

Rather than settling for minimal baseline scripts, several high-impact engineering features were built into the studio:

1. **Zero-Dependency System FFmpeg Auto-Discovery:** Recognizing that macOS hosts often lack Homebrew or system-wide FFmpeg binaries, `pipeline/common.py` implements an autonomous fallback discovery mechanism that leverages `imageio-ffmpeg` to dynamically locate a precompiled Apple Silicon FFmpeg 7.1 binary.
2. **Deterministic SHA-256 Incremental Caching:** Every stage calculates a 16-character SHA-256 digest of its exact inputs. A complete re-run of `make film` executes in **12.7 seconds** with 100% cache hits, enabling live 1-shot regeneration during demonstrations.
3. **Physical Instrument Synthesis in Ethiopian Pentatonic Modes:** Instead of generic Western synthesizer tones, `pipeline/music.py` implements mathematical physical modeling in authentic Ethiopian pentatonic scales:
   - *Tizita Minor* (C, D, Eb, G, Ab)
   - *Bati Major* (C, E, F, G, B)
   - *Anchihoye* (C, Db, F, Gb, A)  
   Synthesizing washint flute vibrato, plucked krar lyre, and nylon guitar created a culturally resonant original score.

---

## 6. Future Roadmap

1. **Multilingual Dubbing Engine:** Expand `pipeline/narration.py` to auto-translate and synchronize parallel narration stems in **Afaan Oromo**, **Tigrinya**, and **Somali**, testing localized prosody across Ethiopian languages.
2. **Family Archival Web Studio:** Package the CLI pipeline into an intuitive Gradio or Web interface where elders and non-technical family members can record voice memories and automatically receive a fully edited heritage short.
3. **Wan 2.2 LoRA Micro-Tuning:** Train a lightweight character LoRA on family archival photos to preserve exact historical likenesses across high-motion diffusion shots.

---

## 7. Submission Checklist & Deliverable Links

| Deliverable | Repository Path / Reference |
| :--- | :--- |
| **Clean Single-Command Run** | `make film` or `python3 run_pipeline.py` |
| **Storyboard Contract & Schema** | [`storyboard.json`](storyboard.json), [`schema/storyboard.schema.json`](schema/storyboard.schema.json) |
| **Telemetry & Call Auditing** | [`runs.jsonl`](runs.jsonl) |
| **Hypothesis Iteration Log** | [`EXPERIMENTS.md`](EXPERIMENTS.md) (11 entries) |
| **Blocker Post-Mortems** | [`FAILURES.md`](FAILURES.md) (5 technical cases) |
| **Cost & Latency Accounting** | [`COSTS.md`](COSTS.md) |
| **Ethics & Consent Record** | [`ETHICS.md`](ETHICS.md) |
| **Final Video Masters** | [`outputs/final/short_vertical_9_16.mp4`](outputs/final/short_vertical_9_16.mp4), [`short_horizontal_16_9.mp4`](outputs/final/short_horizontal_16_9.mp4) |

