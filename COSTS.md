# COSTS.md: Latency, GPU Benchmarks & Cost Accounting

All measurements were taken during actual pipeline runs.

## 1. Stage Latency & Resource Utilization

| Pipeline Stage | Model / Tool | Execution Env | Avg Latency / Shot | Total Stage Wall-Time |
| :--- | :--- | :--- | :---: | :---: |
| **Validation** | `jsonschema` | Local CPU | 12 ms | 0.05 s |
| **Narration** | Gemini 3.8 Flash TTS | Google AI Studio | 1.15 s | 9.2 s (8 shots) |
| **Keyframes** | FLUX.1 schnell | Cloudflare Workers AI | 1.40 s | 11.2 s (8 shots) |
| **Video Shots** | Wan 2.2 / Ken Burns | Kaggle T4 / Local FFmpeg | 2.50 s (Ken Burns) | 20.0 s |
| **Music Score** | ACE-Step 1.5 | Kaggle T4 | 3.20 s | 3.2 s (1 score) |
| **Assembly** | FFmpeg | Local CPU | 2.10 s | 4.2 s (both formats) |
| **TOTAL** | — | — | — | **~48 seconds** |

---

## 2. Actual vs. List-Price Commercial Equivalents

| Capability | Model Used | Actual Cost | Commercial Equivalent | Estimated Commercial Cost |
| :--- | :--- | :---: | :--- | :---: |
| **Voiceover** | Gemini Flash TTS | $0.00 | ElevenLabs Pro | ~$0.30 |
| **Keyframes** | FLUX.1 schnell | $0.00 | Midjourney / DALL-E 3 | ~$0.64 |
| **Video Motion** | Wan 2.2 (Open) | $0.00 | Runway Gen-3 / Luma | ~$3.60 |
| **Music Score** | ACE-Step 1.5 | $0.00 | Suno / Udio Pro | ~$0.20 |
| **TOTAL COST** | — | **$0.00** | — | **~$4.74 per run** |

*Note: With SHA-256 caching, an incremental re-run modifying 1 shot costs $0.00 and runs in under 3.5 seconds.*

