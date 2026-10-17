"""Write the API contract to docs/openapi.json for the frontend team.

Run from backend/ after the feature branches merge:  python scripts/export_openapi.py
"""

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402

OUT = BACKEND_DIR.parent / "docs" / "openapi.json"


def main() -> None:
    OUT.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(BACKEND_DIR.parent)} ({len(app.openapi()['paths'])} paths)")


if __name__ == "__main__":
    main()
