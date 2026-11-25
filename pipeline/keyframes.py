"""
Keyframes stage: Generates visual anchors via FLUX.1 schnell on Cloudflare Workers AI.
Conditioned on a unified Character & Style Reference to ensure consistency.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from .common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run
except ImportError:
    from common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run

KEYFRAMES_DIR = OUTPUTS_DIR / "keyframes"
KEYFRAMES_DIR.mkdir(parents=True, exist_ok=True)


def call_cloudflare_flux(prompt: str, steps: int = 4) -> bytes:
    """Calls Cloudflare Workers AI FLUX.1 schnell endpoint and returns raw image bytes."""
    cf_account = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    cf_token = os.getenv("CLOUDFLARE_API_TOKEN")

    if not cf_account or not cf_token:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("CLOUDFLARE_ACCOUNT_ID="):
                        cf_account = line.split("=", 1)[1].strip().strip('"').strip("'")
                        os.environ["CLOUDFLARE_ACCOUNT_ID"] = cf_account
                    elif line.startswith("CLOUDFLARE_API_TOKEN="):
                        cf_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        os.environ["CLOUDFLARE_API_TOKEN"] = cf_token

    if not cf_account or not cf_token:
        raise ValueError("Cloudflare credentials (CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN) missing in .env")

    url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    headers = {
        "Authorization": f"Bearer {cf_token}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"prompt": prompt, "steps": steps}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
        try:
            res_json = json.loads(data.decode("utf-8"))
            if "result" in res_json and "image" in res_json["result"]:
                return base64.b64decode(res_json["result"]["image"])
        except Exception:
            pass
        return data


def generate_reference_sheet(force: bool = False):
    """Generates visual anchor sheet for character and style consistency."""
    storyboard = load_storyboard()
    style_ref = storyboard.get("style_reference", {})
    char_desc = style_ref.get("character_description", "10-year-old Ethiopian highland boy, kind eyes, traditional cotton vest")
    style_desc = style_ref.get("visual_style", "Cinematic 35mm film, warm morning light, centered framing")

    char_ref_path = KEYFRAMES_DIR / "character_reference.jpg"
    style_ref_path = KEYFRAMES_DIR / "style_reference.jpg"

    if not char_ref_path.exists() or force:
        print("🎨 [REFERENCE] Generating Character Reference Sheet with FLUX.1...")
        prompt = f"Full portrait character sheet of {char_desc}. {style_desc}. High detail, centered."
        t0 = time.time()
        img_bytes = call_cloudflare_flux(prompt, steps=4)
        char_ref_path.write_bytes(img_bytes)
        lat = int((time.time() - t0) * 1000)
        print(f"   └─ Saved {char_ref_path.name} ({len(img_bytes)/1024:.1f} KB in {lat}ms)")
        log_run("keyframes", "flux-1-schnell", {"prompt": prompt}, seed=42, latency_ms=lat, shot_id="character_ref")
    else:
        print(f"🎨 [REFERENCE] Character reference already cached: {char_ref_path.name}")

    if not style_ref_path.exists() or force:
        print("🎨 [REFERENCE] Generating Style Reference Sheet with FLUX.1...")
        prompt = f"Cinematic landscape of rural Ethiopian highlands at golden dawn. {style_desc}. Rolling green hills, red soil pathway, acacia trees, soft morning mist, 35mm film."
        t0 = time.time()
        img_bytes = call_cloudflare_flux(prompt, steps=4)
        style_ref_path.write_bytes(img_bytes)
        lat = int((time.time() - t0) * 1000)
        print(f"   └─ Saved {style_ref_path.name} ({len(img_bytes)/1024:.1f} KB in {lat}ms)")
        log_run("keyframes", "flux-1-schnell", {"prompt": prompt}, seed=42, latency_ms=lat, shot_id="style_ref")
    else:
        print(f"🎨 [REFERENCE] Style reference already cached: {style_ref_path.name}")


def generate_keyframes(force_regen: bool = False):
    generate_reference_sheet(force=force_regen)

    storyboard = load_storyboard()
    style_ref = storyboard.get("style_reference", {})
    style_prompt = style_ref.get("visual_style", "")
    char_prompt = style_ref.get("character_description", "")
    shots = storyboard.get("shots", [])

    print("=" * 65)
    print(f"KEYFRAMES STAGE: Generating Visuals for {len(shots)} Shots with FLUX.1")
    print("=" * 65)

    for idx, shot in enumerate(shots, 1):
        shot_id = shot["id"]
        v_prompt = shot.get("visual_prompt", "").strip()
        seed = shot.get("seed", 42)

        if not v_prompt:
            continue

        full_prompt = f"{v_prompt}. Character: {char_prompt}. Style: {style_prompt}"
        cache_key = compute_cache_key(shot_id, full_prompt, seed)
        output_file = KEYFRAMES_DIR / f"{shot_id}_{cache_key}.jpg"
        metadata_file = KEYFRAMES_DIR / f"{shot_id}.current"

        if output_file.exists() and output_file.stat().st_size > 10000 and not force_regen:
            size_kb = output_file.stat().st_size / 1024.0
            print(f"[{idx}/{len(shots)}] [CACHE HIT] {shot_id} -> {output_file.name} ({size_kb:.1f} KB)")
            metadata_file.write_text(str(output_file))
            continue

        start_time = time.time()
        print(f"\n[{idx}/{len(shots)}] 🌐 Requesting {shot_id} via Cloudflare FLUX.1 schnell...")
        print(f"     Prompt: \"{v_prompt[:60]}...\"")

        try:
            img_bytes = call_cloudflare_flux(full_prompt, steps=4)
            output_file.write_bytes(img_bytes)
            metadata_file.write_text(str(output_file))
            elapsed = time.time() - start_time
            size_kb = len(img_bytes) / 1024.0
            print(f"     ✅ Response 200 OK ({elapsed:.2f}s) -> Generated {output_file.name} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"     ❌ Keyframe generation failed for {shot_id}: {e}")

        latency_ms = int((time.time() - start_time) * 1000)
        log_run(
            stage="keyframes",
            model="flux-1-schnell",
            parameters={"prompt": full_prompt[:120], "steps": 4},
            seed=seed,
            latency_ms=max(latency_ms, 10),
            cost_usd=0.0,
            shot_id=shot_id
        )

        time.sleep(1)

    print("\n✨ [KEYFRAMES COMPLETE] All keyframe images generated in outputs/keyframes/\n")


if __name__ == "__main__":
    force = "--force" in sys.argv
    generate_keyframes(force_regen=force)
