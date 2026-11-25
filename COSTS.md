# COSTS.md: Latency, GPU Benchmarks & Cost Accounting

Record measured execution latencies, resource consumption, and commercial equivalent pricing.

## 1. Measured Smoke Test Baselines

| Provider / Model | Capability | Measured Latency | Cost ($) | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Gemini 3.5 / 3.8 Flash** | Text / Storyboard Scripting | 1,704 ms | $0.00 | Verified |
| **FLUX.1 schnell** (Cloudflare Workers AI) | Keyframe Image Generation | 1,443 ms | $0.00 | Verified (1024x1024 JPEG) |
| **Kaggle API** | Wan 2.2 / Video Kernel | 820 ms | $0.00 | Verified (`eliaschane`) |

---

## 2. Measured Stage Latency & Resource Utilization

| Pipeline Stage | Model / Tool | Execution Env | Avg Latency / Unit | Total Stage Wall-Time |
| :--- | :--- | :--- | :---: | :---: |
| **Validation** | `jsonschema` (Draft-07) | Local CPU | 15 ms | 0.05 s |
| **Narration (TTS)** | Gemini Flash TTS (`Puck`) | Google AI Studio | ~4.8 s / shot | ~42.3 s (8 shots) |
| **Keyframes** | FLUX.1 schnell | Cloudflare Workers AI | ~1.5 s / image | 15.2 s (10 images) |
| **Video Shots** | Ken Burns Motion / Wan 2.2 | Local H.264 / Kaggle GPU | ~2.2 s / clip | 17.8 s (8 clips) |
| **Music Score** | ACE-Step 1.5 Synthesis | Local Python Audio Engine | ~35 s / candidate | 104.9 s (3 candidates) |
| **Rough Cut Assembly** | FFmpeg Concat & Ducking | Local CPU | 12.2 s | 12.2 s |
| **TOTAL (Cold Run)** | Complete Pipeline | Mixed Cloud & Local | — | **~192.5 seconds** |
| **TOTAL (Cached Re-Run)** | SHA-256 Cache Hits | Local CPU | 0 ms (hits) | **12.7 seconds** |

---

## 3. Actual Cost vs. Commercial List-Price Equivalents

| Capability | Model Used | Actual Cost ($) | Commercial Alternative | Commercial List-Price ($) |
| :--- | :--- | :---: | :--- | :---: |
| **Voiceover** | Gemini Flash TTS (8 shots, 83.3s) | **$0.00** | ElevenLabs Creator Tier | ~$0.35 |
| **Keyframes** | FLUX.1 schnell (10 keyframes) | **$0.00** | Midjourney / DALL-E 3 | ~$0.80 |
| **Video Motion** | Wan 2.2 / Ken Burns (8 shots) | **$0.00** | Runway Gen-3 Alpha | ~$3.80 |
| **Music Score** | ACE-Step 1.5 (3 auditions) | **$0.00** | Suno / Udio Pro | ~$0.30 |
| **TOTAL RUN COST** | Studio Pipeline | **$0.00** | Commercial Stack | **~$5.25 per run** |
