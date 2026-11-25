"""
Narration stage: Generates consistent, natural spoken voiceover
Supports:
1. Gemini Flash TTS ('Charon')
2. Native Ethiopian Neural TTS ('am-ET-AmehaNeural') for 100% voice consistency & quota resilience
"""
import argparse
import asyncio
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

try:
    from .common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run
except ImportError:
    from common import BASE_DIR, OUTPUTS_DIR, load_storyboard, compute_cache_key, log_run

NARRATION_DIR = OUTPUTS_DIR / "narration"
NARRATION_DIR.mkdir(parents=True, exist_ok=True)


def assemble_smooth_radio_cut(shot_files: list, output_path: Path, pad_ms: int = 250):
    """
    Stitches per-shot audio files into a seamless master track
    with smooth breath padding between shots.
    """
    if not shot_files:
        return

    # Check if files are wav or mp3
    first_file = shot_files[0]
    if first_file.suffix == ".wav":
        sample_rate = 24000
        channels = 1
        sampwidth = 2
        num_pad_frames = int(sample_rate * (pad_ms / 1000.0))
        silence_frames = b"\x00" * (num_pad_frames * channels * sampwidth)

        with wave.open(str(output_path), "wb") as outfile:
            outfile.setnchannels(channels)
            outfile.setsampwidth(sampwidth)
            outfile.setframerate(sample_rate)

            for i, wav_file in enumerate(shot_files):
                with wave.open(str(wav_file), "rb") as infile:
                    outfile.writeframes(infile.readframes(infile.getnframes()))
                if i < len(shot_files) - 1:
                    outfile.writeframes(silence_frames)

        with wave.open(str(output_path), "rb") as f:
            duration = f.getnframes() / float(f.getframerate())
            print(f"\n✨ [RADIO CUT] Master narration compiled with smooth {pad_ms}ms transitions:")
            print(f"   └─ File: {output_path}")
            print(f"   └─ Duration: {duration:.2f}s ({int(duration//60)}m {int(duration%60)}s)\n")
    else:
        # Binary MP3 concatenation
        with open(output_path, "wb") as outfile:
            for f in shot_files:
                outfile.write(f.read_bytes())
        print(f"\n✨ [RADIO CUT] Master narration compiled: {output_path}")


async def generate_with_edge_tts(text: str, voice: str, output_path: Path, rate: str = "-18%"):
    import edge_tts
    # Slow down speed by 18-20% to achieve calm, natural, unhurried storytelling cadence
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))


def generate_narration(force_regen: bool = False, engine: str = "gemini", voice: str = "Puck", rate: str = "-18%"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        os.environ["GEMINI_API_KEY"] = api_key

    storyboard = load_storyboard()
    shots = storyboard.get("shots", [])

    active_voice = voice or "Puck"
    tts_model = "gemini-2.5-flash-preview-tts" if engine == "gemini" else "edge-tts:am-ET-AmehaNeural"

    print("=" * 65)
    print(f"NARRATION STAGE: Generating Voiceover ({engine.upper()} ENGINE)")
    print(f"Total Shots: {len(shots)} | Voice: {active_voice}")
    print("=" * 65)

    approved_shot_files = []

    for idx, shot in enumerate(shots, 1):
        shot_id = shot["id"]
        narration_info = shot.get("narration", {})
        text = narration_info.get("text", "").strip()
        style = narration_info.get("voice_style", "calm, warm, unhurried")
        seed = shot.get("seed", 42)

        if not text:
            continue

        ext = ".wav" if engine == "gemini" else ".mp3"
        cache_key = compute_cache_key(shot_id, text, style, seed) if engine == "gemini" else compute_cache_key(shot_id, text, style, active_voice, rate, seed)
        audio_output = NARRATION_DIR / f"{shot_id}_{cache_key}{ext}"
        metadata_file = NARRATION_DIR / f"{shot_id}.current"

        # Check Cache
        if audio_output.exists() and audio_output.stat().st_size > 2000 and not force_regen:
            size_kb = audio_output.stat().st_size / 1024.0
            print(f"[{idx}/{len(shots)}] [CACHE HIT] {shot_id} -> {audio_output.name} ({size_kb:.1f} KB)")
            metadata_file.write_text(str(audio_output))
            approved_shot_files.append(audio_output)
            continue

        start_time = time.time()
        print(f"\n[{idx}/{len(shots)}] 🌐 Requesting {shot_id} ({engine.upper()} | speed: {rate})...")
        print(f"     Voice: {active_voice}")
        print(f"     Text : \"{text[:55]}...\"")

        success = False

        if engine == "edge":
            try:
                t0 = time.time()
                asyncio.run(generate_with_edge_tts(text, active_voice, audio_output, rate=rate))
                elapsed = time.time() - t0
                size_kb = audio_output.stat().st_size / 1024.0
                print(f"     ✅ Response 200 OK ({elapsed:.2f}s) -> Generated {audio_output.name} ({size_kb:.1f} KB)")
                metadata_file.write_text(str(audio_output))
                approved_shot_files.append(audio_output)
                success = True
            except Exception as e:
                print(f"     ❌ Edge TTS Error for {shot_id}: {e}")
        else:
            # Gemini Flash TTS
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
            steering_prompt = f"Speak in a gentle, warm, unhurried, natural human storytelling voice with genuine emotional warmth: {text}"
            payload = {
                "contents": [{"parts": [{"text": steering_prompt}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": active_voice}
                        }
                    }
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=35) as resp:
                    elapsed = time.time() - t0
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                    with wave.open(str(audio_output), "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(raw_pcm)
                    metadata_file.write_text(str(audio_output))
                    dur = len(raw_pcm) / 48000.0
                    print(f"     ✅ Response 200 OK ({elapsed:.2f}s) -> Generated {dur:.2f}s audio ({len(raw_pcm)} bytes)")
                    approved_shot_files.append(audio_output)
                    success = True
            except Exception as e:
                print(f"     ❌ Gemini Error for {shot_id}: {e}")

        latency_ms = int((time.time() - start_time) * 1000)
        log_run(
            stage="narration",
            model=tts_model,
            parameters={"text": text, "voice": active_voice, "engine": engine},
            seed=seed,
            latency_ms=max(latency_ms, 10),
            cost_usd=0.0,
            shot_id=shot_id
        )

    # Compile master radio cut
    ext = ".mp3" if engine == "edge" else ".wav"
    master_radio_cut = OUTPUTS_DIR / f"radio_cut_voiceover{ext}"
    assemble_smooth_radio_cut(approved_shot_files, master_radio_cut, pad_ms=250)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate film narration audio")
    parser.add_argument("--force", action="store_true", help="Force regenerate all audio files")
    parser.add_argument("--engine", type=str, default="gemini", choices=["gemini", "edge"], help="TTS engine: 'gemini' (Puck voice matching approved audio) or 'edge'")
    parser.add_argument("--voice", type=str, default=None, help="Voice persona name")
    parser.add_argument("--rate", type=str, default="-18%", help="Speech speed rate (default: '-18%' for calm storytelling)")
    args = parser.parse_args()

    generate_narration(force_regen=args.force, engine=args.engine, voice=args.voice, rate=args.rate)
