from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import osmium
except ImportError as error:
    raise SystemExit("osmium 4.3.1 is required for generation; install requirements.txt") from error

from search_common import GENERATOR_VERSION, normalize_search_text, sha256_file, spatial_bucket, tokenize

NAME_FIELDS = {
    "name": ("primary", "", 100),
    "official_name": ("official", "", 90),
    "short_name": ("short", "", 80),
    "loc_name": ("local", "", 85),
    "alt_name": ("alternate", "", 75),
    "old_name": ("old", "", 50),
}

SETTLEMENTS = {"city", "town", "village", "suburb", "neighbourhood", "quarter", "hamlet"}
ROADS = {"motorway", "trunk", "primary", "secondary", "tertiary", "residential", "unclassified", "living_street", "pedestrian", "service", "path", "footway", "cycleway"}


def classify(tags: dict[str, str]) -> tuple[str, str] | None:
    if tags.get("access") in {"private", "no"} or "military" in tags or tags.get("amenity") == "prison":
        return None
    place = tags.get("place")
    highway = tags.get("highway")
    amenity = tags.get("amenity")
    tourism = tags.get("tourism")
    historic = tags.get("historic")
    if place in SETTLEMENTS:
        return "settlement", place
    if highway in ROADS:
        return "road", highway
    if tags.get("railway") in {"station", "halt"}:
        return "railway_station", tags["railway"]
    if amenity == "bus_station":
        return "bus_station", amenity
    if amenity in {"ferry_terminal"} or tags.get("aeroway") == "aerodrome":
        return "transport", amenity or "aerodrome"
    if amenity == "hospital":
        return "hospital", amenity
    if amenity in {"clinic", "doctors", "pharmacy"}:
        return "health", amenity
    if amenity == "police":
        return "police", amenity
    if amenity == "fire_station":
        return "fire_station", amenity
    if amenity == "fuel":
        return "fuel", amenity
    if amenity in {"charging_station", "parking"}:
        return "vehicle", amenity
    if amenity == "bank":
        return "bank", amenity
    if amenity == "atm":
        return "atm", amenity
    if amenity in {"school", "college", "university"}:
        return "education", amenity
    if amenity in {"restaurant", "cafe", "fast_food"}:
        return "food", amenity
    if tourism in {"hotel", "hostel", "guest_house", "motel"}:
        return "lodging", tourism
    if tourism in {"attraction", "museum", "viewpoint"}:
        return "landmark", tourism
    if amenity in {"place_of_worship", "townhall", "courthouse", "community_centre"}:
        return "landmark", amenity
    if historic in {"monument", "memorial", "castle"}:
        return "landmark", historic
    if tags.get("man_made") == "tower":
        return "landmark", "tower"
    return None


def split_aliases(value: str) -> Iterable[str]:
    for item in value.split(";"):
        item = item.strip()
        if item:
            yield item


def extract_names(tags: dict[str, str]) -> list[tuple[str, str, str, int]]:
    names: list[tuple[str, str, str, int]] = []
    seen: set[tuple[str, str, str]] = set()
    for key, value in tags.items():
        if not value:
            continue
        if key.startswith("name:"):
            kind, language, weight = "localized", key[5:], 85
        elif key in NAME_FIELDS:
            kind, language, weight = NAME_FIELDS[key]
        else:
            continue
        for name in split_aliases(value):
            marker = (name, language, kind)
            if marker not in seen:
                seen.add(marker)
                names.append((name, language, kind, weight))
    return names


def importance(category_id: str, subclass: str, tags: dict[str, str], base: int) -> int:
    score = base
    if category_id == "settlement":
        score += {"city": 20, "town": 15, "village": 8, "suburb": 5}.get(subclass, 0)
        try:
            population = int(tags.get("population", "0").replace(",", ""))
            score += min(15, int(math.log10(max(population, 1)) * 3))
        except ValueError:
            pass
        if tags.get("capital") in {"yes", "2", "4"}:
            score += 10
    elif category_id == "road":
        score += {"motorway": 25, "trunk": 22, "primary": 18, "secondary": 14, "tertiary": 10}.get(subclass, 0)
    return max(0, min(100, score))


class NodeCollector(osmium.SimpleHandler):
    def __init__(self, connection: sqlite3.Connection, bounds: tuple[float, float, float, float], margin: float):
        super().__init__()
        self.connection = connection
        self.west, self.south, self.east, self.north = bounds
        self.margin = margin
        self.pending: list[tuple[int, float, float]] = []
        self.named_nodes: list[tuple[str, int, float, float, dict[str, str]]] = []

    def node(self, node):
        if not node.location.valid():
            return
        lon, lat = node.location.lon, node.location.lat
        if self.west - self.margin <= lon <= self.east + self.margin and self.south - self.margin <= lat <= self.north + self.margin:
            self.pending.append((node.id, lon, lat))
            if len(self.pending) >= 25_000:
                self.flush()
        if self.west <= lon <= self.east and self.south <= lat <= self.north:
            tags = dict(node.tags)
            if tags.get("name") and classify(tags):
                self.named_nodes.append(("node", node.id, lon, lat, tags))

    def flush(self):
        if self.pending:
            self.connection.executemany("INSERT OR REPLACE INTO node_location(node_id, longitude, latitude) VALUES(?,?,?)", self.pending)
            self.connection.commit()
            self.pending.clear()


class WayCollector(osmium.SimpleHandler):
    def __init__(self, connection: sqlite3.Connection, bounds: tuple[float, float, float, float]):
        super().__init__()
        self.connection = connection
        self.west, self.south, self.east, self.north = bounds
        self.node_ids = {row[0] for row in connection.execute("SELECT node_id FROM node_location")}
        self.features: list[tuple[str, int, float, float, dict[str, str]]] = []

    def way(self, way):
        tags = dict(way.tags)
        if not tags.get("name") or not classify(tags):
            return
        refs = [node.ref for node in way.nodes if node.ref in self.node_ids]
        if not refs:
            return
        points: list[tuple[float, float]] = []
        for start in range(0, len(refs), 500):
            chunk = refs[start : start + 500]
            placeholders = ",".join("?" for _ in chunk)
            points.extend(self.connection.execute(f"SELECT longitude, latitude FROM node_location WHERE node_id IN ({placeholders})", chunk))
        inside = [(lon, lat) for lon, lat in points if self.west <= lon <= self.east and self.south <= lat <= self.north]
        if not inside:
            return
        lon = sum(point[0] for point in inside) / len(inside)
        lat = sum(point[1] for point in inside) / len(inside)
        self.features.append(("way", way.id, lon, lat, tags))


def parse_bounds(value: str) -> tuple[float, float, float, float]:
    values = tuple(float(part.strip()) for part in value.split(","))
    if len(values) != 4:
        raise argparse.ArgumentTypeError("bounds must be west,south,east,north")
    west, south, east, north = values
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise argparse.ArgumentTypeError("invalid bounds")
    return values


def build(arguments: argparse.Namespace) -> dict:
    source = arguments.input.resolve()
    output = arguments.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    source_hash = sha256_file(source)
    work_db = output.with_suffix(".node-cache.sqlite")
    if work_db.exists():
        work_db.unlink()
    cache = sqlite3.connect(work_db)
    cache.execute("PRAGMA journal_mode=WAL")
    cache.execute("CREATE TABLE node_location(node_id INTEGER PRIMARY KEY, longitude REAL NOT NULL, latitude REAL NOT NULL)")
    node_collector = NodeCollector(cache, arguments.bounds, arguments.node_margin)
    node_collector.apply_file(str(source))
    node_collector.flush()
    way_collector = WayCollector(cache, arguments.bounds)
    way_collector.apply_file(str(source))
    features = node_collector.named_nodes + way_collector.features

    policy = json.loads(arguments.category_policy.read_text(encoding="utf-8"))
    database = sqlite3.connect(output)
    database.executescript(arguments.schema.read_text(encoding="utf-8"))
    for category_id, definition in policy["categories"].items():
        database.execute(
            "INSERT INTO category VALUES(?,?,?,?,?,?,?)",
            (category_id, definition["displayGroup"].lower(), category_id, definition["displayGroup"], definition["displayName"], definition["iconKey"], definition["defaultImportance"]),
        )
    west, south, east, north = arguments.bounds
    database.execute(
        "INSERT INTO metadata VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (arguments.search_index_id, 1, arguments.data_version, arguments.package_id, west, south, east, north, arguments.source_url, arguments.source_timestamp, source_hash, "© OpenStreetMap contributors", "Open Database License 1.0", "https://www.openstreetmap.org/copyright", GENERATOR_VERSION, arguments.created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")),
    )
    category_counts: dict[str, int] = {}
    for source_type, source_id, lon, lat, tags in features:
        classification = classify(tags)
        if not classification:
            continue
        category_id, subclass = classification
        primary_name = tags["name"].strip()
        normalized_primary = normalize_search_text(primary_name)
        if not normalized_primary:
            continue
        category_base = int(policy["categories"][category_id]["defaultImportance"])
        locality = tags.get("addr:city") or tags.get("addr:suburb") or tags.get("is_in:city")
        cursor = database.execute(
            "INSERT OR IGNORE INTO place(source_type,source_id,package_id,primary_name,normalized_primary_name,category_id,subclass,latitude,longitude,importance,admin_id,locality,spatial_bucket) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (source_type, source_id, arguments.package_id, primary_name, normalized_primary, category_id, subclass, lat, lon, importance(category_id, subclass, tags, category_base), None, locality, spatial_bucket(lat, lon)),
        )
        if cursor.rowcount != 1:
            continue
        place_id = cursor.lastrowid
        category_counts[category_id] = category_counts.get(category_id, 0) + 1
        for name, language, kind, weight in extract_names(tags):
            normalized = normalize_search_text(name)
            if not normalized:
                continue
            name_cursor = database.execute(
                "INSERT OR IGNORE INTO place_name(place_id,name,normalized_name,language,name_kind,field_weight) VALUES(?,?,?,?,?,?)",
                (place_id, name, normalized, language, kind, weight),
            )
            if name_cursor.rowcount != 1:
                continue
            name_id = name_cursor.lastrowid
            database.executemany(
                "INSERT OR IGNORE INTO search_token(token,place_id,name_id,field_weight) VALUES(?,?,?,?)",
                [(token, place_id, name_id, weight) for token in sorted(set(tokenize(name)))],
            )
    database.commit()
    database.execute("ANALYZE")
    database.execute("PRAGMA optimize")
    database.commit()
    counts = {
        "places": database.execute("SELECT COUNT(*) FROM place").fetchone()[0],
        "names": database.execute("SELECT COUNT(*) FROM place_name").fetchone()[0],
        "tokens": database.execute("SELECT COUNT(*) FROM search_token").fetchone()[0],
        "categories": dict(database.execute("SELECT category_id, COUNT(*) FROM place GROUP BY category_id ORDER BY category_id")),
    }
    database.close()
    cache.close()
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(str(work_db) + suffix)
        if candidate.exists():
            candidate.unlink()
    result = {"output": str(output), "sourceSha256": source_hash, "outputSha256": sha256_file(output), "outputBytes": output.stat().st_size, **counts}
    arguments.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a DK Offline Map companion search index from a pinned OSM PBF extract.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--bounds", type=parse_bounds, required=True)
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--search-index-id", required=True)
    parser.add_argument("--data-version", type=int, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-timestamp", required=True)
    parser.add_argument("--created-at", help="Pinned UTC build timestamp for reproducible release generation")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--node-margin", type=float, default=0.02)
    script_dir = Path(__file__).resolve().parent
    parser.add_argument("--schema", type=Path, default=script_dir / "schema-v1.sql")
    parser.add_argument("--category-policy", type=Path, default=script_dir / "category-policy-v1.json")
    arguments = parser.parse_args()
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps(build(arguments), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
