from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

GENERATOR_VERSION = "1.0.0"
APPLICATION_ID = 0x444B5331
SCHEMA_VERSION = 1


def sha256_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_latin(char: str) -> bool:
    if not char:
        return False
    return "LATIN" in unicodedata.name(char, "")


def normalize_search_text(value: str) -> str:
    """Match Android's planned NFKC/case-fold normalization without damaging Indic marks."""
    value = unicodedata.normalize("NFKC", value.strip()).casefold()
    decomposed = unicodedata.normalize("NFKD", value)
    output: list[str] = []
    last_base = ""
    for char in decomposed:
        category = unicodedata.category(char)
        if category.startswith("M"):
            if _is_latin(last_base):
                continue
            output.append(char)
            continue
        if category.startswith(("P", "S", "Z")) or char.isspace():
            output.append(" ")
            last_base = ""
            continue
        output.append(char)
        last_base = char
    return unicodedata.normalize("NFKC", re.sub(r"\s+", " ", "".join(output)).strip())


def tokenize(value: str) -> list[str]:
    return [part for part in normalize_search_text(value).split(" ") if part]


def prefix_upper_bound(prefix: str) -> str:
    if not prefix:
        raise ValueError("prefix must not be empty")
    points = [ord(char) for char in prefix]
    for index in range(len(points) - 1, -1, -1):
        if points[index] < 0x10FFFF:
            points[index] += 1
            return "".join(chr(point) for point in points[: index + 1])
    raise ValueError("prefix has no finite Unicode upper bound")


def spatial_bucket(latitude: float, longitude: float) -> int:
    lat_bucket = int((latitude + 90.0) * 100)
    lon_bucket = int((longitude + 180.0) * 100)
    return lat_bucket * 36000 + lon_bucket
