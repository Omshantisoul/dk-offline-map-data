from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from search_common import sha256_file


def md5_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sidecar(path: Path) -> str:
    return path.read_text(encoding="ascii").strip().split()[0].lower()


def verify(path: Path, expected_bytes: int, expected_md5: str | None, sidecar: Path | None, expected_sha256: str | None) -> dict:
    actual_md5 = md5_file(path)
    expected_sidecar_md5 = read_sidecar(sidecar) if sidecar else None
    actual_sha256 = sha256_file(path)
    checks = {
        "bytes": path.stat().st_size == expected_bytes,
        "md5": expected_md5 is None or actual_md5 == expected_md5.lower(),
        "sidecarMd5": expected_sidecar_md5 is None or actual_md5 == expected_sidecar_md5,
        "sha256": expected_sha256 is None or actual_sha256 == expected_sha256.lower(),
    }
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "md5": actual_md5, "sha256": actual_sha256, "checks": checks, "valid": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--florence", type=Path, required=True)
    parser.add_argument("--florence-md5", type=Path, required=True)
    parser.add_argument("--bengaluru", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    results = {
        "florence": verify(arguments.florence, 379_876_352, None, arguments.florence_md5, None),
        "bengaluru": verify(arguments.bengaluru, 554_472_408, "a4b4bd58527414b456dfccb96548e3e5", None, "2e929462d4d232f8d1f2f3182481f8ba2656f0fa1677e2238e3fe0b73107195b"),
    }
    results["valid"] = all(item["valid"] for item in results.values())
    rendered = json.dumps(results, indent=2) + "\n"
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
