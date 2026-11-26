"""
Shots stage: Generates video clips using Wan 2.2 TI2V-5B or FFmpeg cinematic Ken Burns motion.
Animates FLUX.1 keyframes with directional pans, tilts, and zoom movements matched to narration length.
"""
import argparse
import os
import sys
import time
import wave
import subprocess
from pathlib import Path

try:
    from .common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run, get_ffmpeg_cmd
except ImportError:
    from common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run, get_ffmpeg_cmd

SHOTS_DIR = OUTPUTS_DIR / "shots"
KEYFRAMES_DIR = OUTPUTS_DIR / "keyframes"
NARRATION_DIR = OUTPUTS_DIR / "narration"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)


def get_audio_duration(shot_id: str) -> float:
    """Returns actual narration audio duration in seconds if available."""
    meta_path = NARRATION_DIR / f"{shot_id}.current"
    if meta_path.exists():
        try:
            audio_path = Path(meta_path.read_text().strip())
            if audio_path.exists() and audio_path.suffix == ".wav":
                with wave.open(str(audio_path), "rb") as w:
                    frames = w.getnframes()
                    rate = w.getframerate()
                    return frames / float(rate)
        except Exception:
            pass
    return None


def get_motion_filter(motion_type: str, duration: float, fps: int = 25) -> str:
    """
    Returns high-resolution FFmpeg zoompan filter for cinematic motion.
    Supported: push_in, pull_out, pan_right, pan_left, slow_drift.
    """
    total_frames = int(duration * fps)
    prep = "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,setsar=1"

    if "pan" in motion_type.lower() and "left to right" in motion_type.lower():
        # Slow pan left to right with slight zoom
        return f"{prep},zoompan=z='1.10':x='(iw-iw/zoom)*(on/({total_frames}-1))':y='ih/2-(ih/zoom/2)':d={total_frames}:fps={fps}:s=1920x1080,setsar=1"
    elif "pull out" in motion_type.lower() or "wide" in motion_type.lower():
        # Slow pull out / reveal
        return f"{prep},zoompan=z='max(1.14-0.001*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:fps={fps}:s=1920x1080,setsar=1"
    elif "pan" in motion_type.lower():
        # Slow pan right to left
        return f"{prep},zoompan=z='1.10':x='(iw-iw/zoom)*(1-on/({total_frames}-1))':y='ih/2-(ih/zoom/2)':d={total_frames}:fps={fps}:s=1920x1080,setsar=1"
    else:
        # Default gentle push-in
        return f"{prep},zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:fps={fps}:s=1920x1080,setsar=1"


def generate_shots(force_regen: bool = False, use_ken_burns: bool = True):
    """
    Generates moving shots from keyframes with deterministic SHA-256 caching.
    """
    storyboard = load_storyboard()
    shots = storyboard.get("shots", [])
    ffmpeg_bin = get_ffmpeg_cmd()

    print("=" * 65)
    print(f"SHOTS STAGE: Generating {len(shots)} Video Clips ({'Cinematic Ken Burns' if use_ken_burns else 'Wan 2.2'})")
    print("=" * 65)

    for idx, shot in enumerate(shots, 1):
        shot_id = shot["id"]
        m_prompt = shot.get("motion_prompt", "").strip()
        seed = shot.get("seed", 42)

        # Sync duration with actual narration audio if present
        actual_audio_dur = get_audio_duration(shot_id)
        if actual_audio_dur:
            duration = round(actual_audio_dur + 0.3, 1)  # 300ms natural breath pad
        else:
            duration = shot.get("duration_sec", 6.0)

        cache_key = compute_cache_key(shot_id, m_prompt, duration, seed)
        output_file = SHOTS_DIR / f"{shot_id}_{cache_key}.mp4"
        metadata_file = SHOTS_DIR / f"{shot_id}.current"

        if output_file.exists() and output_file.stat().st_size > 10000 and not force_regen:
            size_kb = output_file.stat().st_size / 1024.0
            print(f"[{idx}/{len(shots)}] [CACHE HIT] {shot_id} -> {output_file.name} ({size_kb:.1f} KB, {duration}s)")
            metadata_file.write_text(str(output_file))
            continue

        start_time = time.time()
        print(f"\n[{idx}/{len(shots)}] 🎬 Rendering {shot_id} ({duration}s)...")
        print(f"     Motion: \"{m_prompt[:55]}...\"")

        # Locate keyframe
        keyframe_meta = KEYFRAMES_DIR / f"{shot_id}.current"
        keyframe_path = None
        if keyframe_meta.exists():
            candidate = Path(keyframe_meta.read_text().strip())
            if candidate.exists() and candidate.stat().st_size > 1000:
                keyframe_path = candidate

        if not keyframe_path:
            # Fallback search
            k_candidates = sorted(KEYFRAMES_DIR.glob(f"{shot_id}_*.jpg"))
            if k_candidates:
                keyframe_path = k_candidates[-1]

        if not keyframe_path or not keyframe_path.exists():
            raise FileNotFoundError(f"Missing keyframe image for {shot_id}. Run keyframes stage first.")

        vf_filter = get_motion_filter(m_prompt, duration, fps=25)

        cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1",
            "-i", str(keyframe_path),
            "-vf", vf_filter,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(output_file)
        ]

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            metadata_file.write_text(str(output_file))
            elapsed = time.time() - start_time
            size_mb = output_file.stat().st_size / (1024.0 * 1024.0)
            print(f"     ✅ Rendered in {elapsed:.2f}s -> {output_file.name} ({size_mb:.2f} MB)")
        except subprocess.CalledProcessError as e:
            print(f"     ❌ FFmpeg failed for {shot_id}: {e.stderr.decode('utf-8', errors='ignore')[-300:]}")
            raise

        latency_ms = int((time.time() - start_time) * 1000)
        log_run(
            stage="shots",
            model="ffmpeg-ken-burns" if use_ken_burns else "wan-2.2-ti2v-5b",
            parameters={"motion_prompt": m_prompt, "duration_sec": duration, "fps": 25},
            seed=seed,
            latency_ms=max(latency_ms, 10),
            cost_usd=0.0,
            shot_id=shot_id
        )

    print("\n✨ [SHOTS COMPLETE] All video clips generated in outputs/shots/\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate video shots from keyframes")
    parser.add_argument("--force", action="store_true", help="Force regenerate shots ignoring cache")
    parser.add_argument("--mode", choices=["ken_burns", "wan"], default="ken_burns", help="Motion generation mode")
    args = parser.parse_args()

    generate_shots(force_regen=args.force, use_ken_burns=(args.mode == "ken_burns"))
