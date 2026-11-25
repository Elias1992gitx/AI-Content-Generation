"""
Validates storyboard.json against schema/storyboard.schema.json
"""
import json
import sys
from pathlib import Path
try:
    from jsonschema import validate, ValidationError
except ImportError:
    validate = None
    ValidationError = Exception

BASE_DIR = Path(__file__).resolve().parent.parent


def validate_storyboard(storyboard_path=None, schema_path=None) -> bool:
    s_path = Path(storyboard_path) if storyboard_path else (BASE_DIR / "storyboard.json")
    sc_path = Path(schema_path) if schema_path else (BASE_DIR / "schema" / "storyboard.schema.json")

    if not s_path.exists():
        print(f"[VALIDATE ERROR] storyboard.json missing at {s_path}")
        return False
    if not sc_path.exists():
        print(f"[VALIDATE ERROR] schema missing at {sc_path}")
        return False

    with open(s_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    with open(sc_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    if validate is None:
        # Fallback basic structural verification if jsonschema package is not installed yet
        print("[WARN] jsonschema not installed, performing basic key check.")
        required_keys = ["title", "target_duration_sec", "language", "shots", "music_cues"]
        for k in required_keys:
            if k not in storyboard:
                print(f"[VALIDATE ERROR] missing key: {k}")
                return False
        if len(storyboard.get("shots", [])) < 8:
            print("[VALIDATE ERROR] storyboard requires at least 8 shots")
            return False
        print("[VALIDATE SUCCESS] Basic schema checks passed.")
        return True

    try:
        validate(instance=storyboard, schema=schema)
        print(f"[VALIDATE SUCCESS] {s_path.name} conforms to {sc_path.name}")
        return True
    except ValidationError as e:
        print(f"[VALIDATE ERROR] Schema validation failed: {e.message} at path: {list(e.path)}")
        return False


if __name__ == "__main__":
    success = validate_storyboard()
    sys.exit(0 if success else 1)

