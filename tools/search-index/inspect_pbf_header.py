from __future__ import annotations

import argparse
import json
from pathlib import Path

import osmium


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    arguments = parser.parse_args()
    reader = osmium.io.Reader(str(arguments.source), osmium.osm.NODE)
    header = reader.header()
    box = header.box()
    result = {
        "path": str(arguments.source.resolve()),
        "hasMultipleObjectVersions": header.has_multiple_object_versions,
        "bounds": [box.bottom_left.lon, box.bottom_left.lat, box.top_right.lon, box.top_right.lat] if box.valid() else None,
        "generator": header.get("generator"),
        "osmosisReplicationTimestamp": header.get("osmosis_replication_timestamp"),
        "osmosisReplicationSequenceNumber": header.get("osmosis_replication_sequence_number"),
        "osmosisReplicationBaseUrl": header.get("osmosis_replication_base_url"),
    }
    reader.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
