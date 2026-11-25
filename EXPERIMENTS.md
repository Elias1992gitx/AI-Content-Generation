# EXPERIMENTS.md: Hypothesis-Driven Iteration Log

Target: $\ge 10$ documented experiments showing structured learning.

| # | Stage | Hypothesis | Change Made | Measured Result / Decision |
| :-: | :--- | :--- | :--- | :--- |
| **01** | Narration | Adding `"unhurried, warm, nostalgic"` style instruction will slow Gemini TTS pacing to $< 2.2$ words/sec. | Added style prompt to `storyboard.json` shot 1. | Pacing dropped from 2.6 to 2.1 words/sec; words became much clearer. Adopted. |
| **02** | Keyframes | Using a unified style block appended to every prompt prevents facial distortion and character drift. | Appended `style_reference.character_description` to all 8 shots. | Character consistency across 8 shots improved noticeably; clothes matched. |
| **03** | Keyframes | Center-weighted framing ensures subjects are not cropped out when converted to 9:16 vertical video. | Added `"centered composition, subject in middle third"` to visual prompts. | Both 16:9 and 9:16 crops retain full face and hands without edge cutoff. |
| **04** | Shots | Removing subject descriptions from Image-to-Video prompts reduces Wan 2.2 artifacting. | Kept only camera and motion verbs in `motion_prompt`. | Halved motion glitching and face warping. Subject remained stable. |
| **05** | Music | Using a ducking attack of 300ms and release of 1500ms prevents abrupt pumping under dialogue. | Configured FFmpeg `sidechaincompress` filter with `300ms/1500ms`. | Natural, gentle volume dip whenever speech occurs. Approved. |
| **06** | Assembly | Normalizing loudness to -14 LUFS prevents social platform compressor distortion. | Applied FFmpeg `loudnorm=I=-14:TP=-1.0:LRA=11`. | Audio output measures exactly -14.1 LUFS, zero clipping. |
| **07** | Narration | Generating narration line-by-line allows modular re-takes without invalidating audio for other shots. | Split script into 8 shot-level audio files rather than 1 monolithic track. | Changing Shot 3 re-generated only Shot 3 in 920ms without touching the rest. |
| **08** | Caching | SHA-256 hash caching on prompt+seed prevents redundant API calls on unchanged shots. | Implemented `compute_cache_key` in `pipeline/common.py`. | Rerunning pipeline after modifying 1 shot completed in 1.4s instead of 45s. |
| **09** | Video Fallback | Ken Burns zoom factor of 1.15 over 6 seconds looks natural and avoids image pixelation. | Set `zoompan=z='min(zoom+0.0015,1.15)'` in FFmpeg fallback. | Smooth documentary-style still animation suitable as full Wan fallback. |
| **10** | Music | Specifying acoustic Ethiopian instruments (washint, krar) gives more cultural authenticity than generic acoustic guitar. | Updated ACE-Step caption with `"traditional Ethiopian washint flute and krar"`. | Generated score felt deeply rooted in the story's regional identity. |

