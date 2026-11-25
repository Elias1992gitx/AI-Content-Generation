#!/usr/bin/env python3
"""
Master Pipeline Entry Point: runs the complete AI-Content-Generation studio.
Usage:
    python run_pipeline.py [--force] [--stage STAGE]
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline.validate import validate_storyboard
from pipeline.narration import generate_narration
from pipeline.keyframes import generate_keyframes
from pipeline.shots import generate_shots
from pipeline.music import generate_music
from pipeline.assemble import assemble_film


def run_pipeline(force: bool = False, stage: str = None):
    print("=" * 60)
    print("AI-CONTENT-GENERATION: The Heritage Short Pipeline")
    print("=" * 60)

    # 1. Validation
    if not validate_storyboard():
        print("[ERROR] Storyboard validation failed. Aborting.")
        sys.exit(1)

    if stage and stage not in ["narration", "keyframes", "shots", "music", "assemble"]:
        print(f"[ERROR] Unknown stage: {stage}")
        sys.exit(1)

    # 2. Stage Execution
    if not stage or stage == "narration":
        generate_narration(force_regen=force)
    if not stage or stage == "keyframes":
        generate_keyframes(force_regen=force)
    if not stage or stage == "shots":
        generate_shots(force_regen=force)
    if not stage or stage == "music":
        generate_music(force_regen=force)
    if not stage or stage == "assemble":
        assemble_film()

    print("=" * 60)
    print("[PIPELINE COMPLETE] Film generated successfully in outputs/final/")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Heritage Short AI pipeline")
    parser.add_argument("--force", action="store_true", help="Force regenerate all assets, ignoring cache")
    parser.add_argument("--stage", type=str, help="Run only a specific stage")
    args = parser.parse_args()

    run_pipeline(force=args.force, stage=args.stage)

