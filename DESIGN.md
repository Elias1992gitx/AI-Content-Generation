# DESIGN.md: Audience, Intent, and Testing Log

## 1. Audience & Emotional Intent
* **Film Title:** The Boy Who Grew with the Land (ከመሬቱ ጋር ያደገው ልጅ)
* **Target Audience:**
  1. Family and relatives who honor my father's journey.
  2. The Ethiopian diaspora and urban youth who may be disconnected from the agricultural roots and rural hardships that built our families.
  3. General viewers who appreciate intergenerational gratitude and cultural heritage storytelling.
* **Viewing Context:**
  * Primarily mobile vertical (9:16) on TikTok, Instagram Reels, and Telegram family channels.
  * Cinematic landscape (16:9) on YouTube.
* **Core Emotional Objective:**
  * To evoke deep reverence and pride. By the end, the viewer should feel that manual farming and childhood responsibility were not just struggles, but the foundational school of character: *"Some people inherit wealth, some inherit knowledge, but my father inherited the strength of the land."*

---

## 2. Shot Rationale Summary (8 Narrative Beats)
Every shot in `storyboard.json` exists for a concrete narrative and emotional reason:

1. **Shot 1 (Extreme Wide - Dawn in the Highlands):**
   * *Rationale:* Establishes place, tranquility, and historical time. Visualizes the wide Ethiopian countryside before the noise of modern cities.
2. **Shot 2 (Medium - The Young Boy Waking at Dew):**
   * *Rationale:* Introduces our young protagonist. Shows him barefoot stepping into the cool morning grass, ready to work before sunrise.
3. **Shot 3 (Wide - Guiding the Cattle & Sheep):**
   * *Rationale:* Establishes childhood responsibility. He is not playing with toys; he is shepherding livestock through rolling green hills.
4. **Shot 4 (Close-Up - Planting Seeds into Red Soil):**
   * *Rationale:* Symbolizes hope, patience, and learning from the earth. The hands touching the soil emphasize his direct connection with the land.
5. **Shot 5 (Wide - Communal Harvest & Community Solidarity):**
   * *Rationale:* Shows the Ethiopian cultural value of *Debo* (communal labor), neighbors helping one another, proving life was sustained through togetherness.
6. **Shot 6 (Close-Up Portrait - Weathered Young Smile under the Sun):**
   * *Rationale:* Emotional peak. Despite the fatigue, his eyes shine with determination and dignity beneath the vast Ethiopian sky.
7. **Shot 7 (Medium - The Boy Looking into the Horizon at Sunset):**
   * *Rationale:* The transition from childhood to adulthood. The little boy who walked the fields preparing to carry that strength into the future.
8. **Shot 8 (Wide / Resolution - The Land Remembers His Footsteps):**
   * *Rationale:* Legacy and philosophical conclusion. His footsteps remain in the land; his children carry forward his enduring resilience.

---

## 3. User Test 1: The Radio Cut (Narration + Temp Audio)
* **Date:** 2026-11-25
* **Format:** Spoken Amharic voiceover animatic played in person to target audience members.
* **Audience Participants:** (3 real listeners)
  1. *Listener 1 (Family Member):* "The voice changes in between the shots—it is not consistent across the story."
  2. *Listener 2 (Peer / Relative):* "The first voice is nice and warm, but the second voice is not good. Make the voice consistent throughout."
  3. *Listener 3 (Friend / Native Speaker):* "Make the voice and story transition smooth between the scenes so it flows like a single memory."

### Concrete Changes Made to `storyboard.json` and Pipeline Based on Test 1:
* **Change 1 (Voice Consistency):** Locked the voice persona strictly to **`Charon`** across every single shot. Retired the higher-pitched voice (`Puck`) entirely so one consistent elder narrator voices the entire film.
* **Change 2 (Audio Smoothing & Pacing):** Added natural breath pauses and 200ms audio cross-fades between shots in the assembly stage so narration transitions sound seamless rather than abrupt cuts.
* **Change 3 (Refined Agricultural Cadence):** Polished the phrasing in Shot 3 and Shot 4 to ensure a smooth storytelling transition from pasture herding to seed cultivation.

---

## 4. User Test 2: Near-Final Cut (Visuals + Ducking + Subtitles)
* **Date:** [Scheduled for Phase 3]
* **Audience Participants:** (3 target viewers)
  1. *Viewer 1:* [Feedback on subtitle readability and pacing]
  2. *Viewer 2:* [Feedback on visual consistency of the young boy across shots]
  3. *Viewer 3:* [Feedback on music ducking under narration]

### Concrete Refinements Made Before Final Export:
* **Change 1:** [Recorded in Phase 3]
* **Change 2:** [Recorded in Phase 3]
