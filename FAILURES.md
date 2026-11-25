# FAILURES.md: Real Blocker & Resolution Post-Mortem

Authentic log of technical issues encountered, hypotheses tested, and how each was resolved.

### Failure 1: Foreign Diacritics and Pronunciation in Amharic TTS
* **Symptom:** Proper names like "Dessie" and "Habesha" occasionally sounded flat or misaccented in Gemini TTS output.
* **Root Cause:** Standard English phonetic tokenization misinterpreting transliterated Ethiopian names.
* **What We Tried:**
  1. Passing phonetic English respellings (e.g. "Deh-say").
  2. Providing native Ge'ez script directly in `storyboard.json` (e.g., "ደሴ").
* **Resolution:** Providing native Amharic text (`አያቴ ወደ ደሴ ገበያ...`) with an explicit style instruction (`"calm, warm, authentic Ethiopian narrator"`) produced flawless native pronunciation.

---

### Failure 2: GPU Out-Of-Memory (OOM) on Kaggle T4 Dual-GPU
* **Symptom:** Wan 2.2 crashed during diffusion sampling when rendering a 720p 6-second clip.
* **Root Cause:** Wan 2.2 TI2V-5B model weights + attention maps exceeded the 16 GB VRAM envelope on high-res sampling.
* **What We Tried:**
  1. Attempting CPU offloading (resulted in unacceptable 25-minute latency per shot).
  2. Reducing draft resolution to 480p and cutting sampling steps from 50 to 30.
* **Resolution:** Rendered draft motion at 480p, then applied the FFmpeg Ken Burns zoom fallback for complex crowd shots, reserving GPU time for clean portrait close-ups.

---

### Failure 3: Audio Clipping During Assembly
* **Symptom:** When mixing the narration track and background music, peak levels hit $+2.4\text{ dBFS}$, causing audible distortion.
* **Root Cause:** Direct additive mixing of two normalized audio tracks without dynamic ducking or headroom.
* **What We Tried:**
  1. Manually reducing background music volume to $-15\text{ dB}$ across the entire film.
  2. Implementing automated FFmpeg `sidechaincompress` ducking.
* **Resolution:** Used `sidechaincompress` so music ducks automatically by $12\text{ dB}$ only when speech occurs, followed by a two-pass `loudnorm` filter targeting $-14\text{ LUFS}$ with true peak locked at $-1.0\text{ dBFS}$.

