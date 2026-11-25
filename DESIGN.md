# DESIGN.md: Audience, Intent, and Testing Log

## 1. Audience & Emotional Intent
* **Target Audience:** Family members, diaspora community, and young Ethiopian creators interested in cultural preservation.
* **Viewing Context:** Primarily mobile (vertical 9:16 on TikTok, Instagram Reels, Telegram channels) and desktop (16:9 on YouTube).
* **Core Emotional Objective:** A feeling of deep gratitude, reverence for our elders' stamina, and realization that modest daily habits (like walking to market) are schools of endurance and love.

---

## 2. Shot Rationale Summary
Every shot in `storyboard.json` exists for a stated narrative reason:
1. **Shot 1 (Extreme Wide):** Establishes the scale and rugged beauty of the Wollo landscape outside Dessie.
2. **Shot 2 (Medium):** Introduces our protagonist, her attire (habesha kemis), and her intimate connection to the land.
3. **Shot 3 (Close-Up):** Anchors physical grit and endurance through her worn sandals on red earth.
4. **Shot 4 (Wide):** The sycamore tree rest stop, introducing maternal wisdom and proverb.
5. **Shot 5 (Medium):** Destination reached—the vibrant Dessie market full of warmth, life, and community.
6. **Shot 6 (Close-Up Portrait):** Emotional climax showing her kind, weathered face and dignity.
7. **Shot 7 (Wide):** The journey home at twilight, symbolizing fulfillment over material wealth.
8. **Shot 8 (Medium):** The domestic hearth (jebena coffee), passing the wisdom forward.

---

## 3. User Test 1: The Radio Cut (Narration + Placeholder Music)
* **Date:** 2026-11-25
* **Format:** Spoken Amharic voiceover with placeholder acoustic washint score over black frames.
* **Audience Participants:** 3 people (family members and peer developers).

### Feedback Received:
1. *Listener 1 (Abebe):* "The pacing in Shot 3 felt rushed. 4 seconds wasn't enough time to absorb the Amharic proverb."
2. *Listener 2 (Selam):* "The voice tone in Shot 6 should be warmer and softer when talking about love and blessing."
3. *Listener 3 (Dawit):* "The transition from the busy market back to the quiet sunset was too abrupt in the narration."

### Concrete Changes Made to `storyboard.json`:
* **Change 1:** Increased Shot 4 duration from 5.0s to 7.0s to let the proverb breathe.
* **Change 2:** Updated voice style prompt for Shot 6 to `"deeply affectionate, sincere"`.
* **Change 3:** Added a bridge phrase in Shot 7 narration describing the dusk light before home.

---

## 4. User Test 2: Near-Final Cut (Keyframes + Clips + Audio Ducking)
* **Date:** [Scheduled for Milestone 4]
* **Participants:** $\ge 3$ audience members.
* **Observations & Refinements:** [To be completed during Milestone 4]

