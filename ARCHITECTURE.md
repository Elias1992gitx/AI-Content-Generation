# ARCHITECTURE.md: Pipeline Design & Contracts

## 1. System Overview
The pipeline functions as a decoupled, automated film studio operating around one central contract: `storyboard.json`.

```
                    ┌─────────────────────────┐
                    │     storyboard.json     │  ◄── Single Source of Truth
                    │ (Validated with Schema) │
                    └───────────┬─────────────┘
                                │
        ┌──────────────┬────────┼──────────────┬──────────────┐
        ▼              ▼        ▼              ▼              ▼
   [keyframes]      [shots]  [narration]    [music]      [assemble]
 (FLUX Schnell)   (Wan 2.2)    (TTS)     (ACE-Step 1.5) (FFmpeg Mix)
        │              │        │              │              │
        └──────────────┴────────┴──────────────┴──────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │       runs.jsonl        │  ◄── Telemetry per model call
                    └─────────────────────────┘
```

---

## 2. Stage Contracts & Data Flow
1. **Validation (`pipeline/validate.py`):**
   - Validates `storyboard.json` against `schema/storyboard.schema.json`.
   - Halts pipeline if durations, required fields, or shot counts are invalid.
2. **Narration (`pipeline/narration.py`):**
   - Inputs: `shots[i].narration.text`, `shots[i].narration.voice_style`.
   - Outputs: `outputs/narration/{shot_id}_{hash}.mp3`.
3. **Keyframes (`pipeline/keyframes.py`):**
   - Inputs: `style_reference`, `shots[i].visual_prompt`, `shots[i].seed`.
   - Outputs: `outputs/keyframes/{shot_id}_{hash}.png`.
4. **Shots (`pipeline/shots.py`):**
   - Inputs: Keyframe image + `shots[i].motion_prompt`.
   - Outputs: `outputs/shots/{shot_id}_{hash}.mp4`.
5. **Music (`pipeline/music.py`):**
   - Inputs: `music_cues.caption`, `tempo_bpm`, `target_duration_sec`.
   - Outputs: `outputs/music/score_{hash}.mp3`.
6. **Assembly (`pipeline/assemble.py`):**
   - Combines video shots, burns English subtitles, ducks score under narration, normalizes audio to -14 LUFS, and outputs 9:16 & 16:9 MP4s.

---

## 3. Caching & Incremental Re-runs
* Every stage uses a deterministic SHA-256 hash of its inputs:
  $$\text{CacheKey} = \text{SHA256}(\text{shot\_id} + \text{prompt} + \text{parameters} + \text{seed})[:16]$$
* If `{shot_id}_{hash}.ext` exists, the stage skips generation and uses the cached file.
* Editing a single shot only re-runs that shot; all others are served from cache in $< 100\text{ ms}$.

---

## 4. Failure Handling & Circuit Breakers
* **Kaggle GPU Quota / Timeout:** If Wan 2.2 is unavailable or queued, `pipeline/shots.py` triggers the FFmpeg Ken Burns pan-and-zoom fallback to generate dynamic camera motion over the keyframe still.
* **Rate Limits:** Automatic exponential backoff (1s, 2s, 4s) up to 3 retries on cloud endpoints.

