# Phase 7 search-index generation

## Toolchain

- Python 3.12.13
- SQLite 3.50.4 (Python standard library)
- osmium/pyosmium 4.3.1
- generator version 1.0.0

Install the pinned generator dependency:

```powershell
python -m pip install --target work\phase7-tools -r tools\search-index\requirements.txt
$env:PYTHONPATH = "work\phase7-tools"
```

Generate Florence:

```powershell
python tools\search-index\build_search_index.py `
  --input sources\centro-260701.osm.pbf `
  --bounds "11.221144,43.745121,11.287543,43.789306" `
  --package-id protomaps_firenze_developer_test `
  --search-index-id florence-test-search `
  --data-version 1 `
  --source-url "https://download.geofabrik.de/europe/italy/centro-260701.osm.pbf" `
  --source-timestamp "2026-07-01T20:22:00Z" `
  --created-at "2026-07-17T11:52:20Z" `
  --output out\florence-test-search-v1.sqlite `
  --report reports\florence-generation.json
```

Generate Bengaluru Central:

```powershell
python tools\search-index\build_search_index.py `
  --input sources\southern-zone-260701.osm.pbf `
  --bounds "77.55,12.92,77.68,13.05" `
  --package-id osm_in_ka_bengaluru_central_developer_test `
  --search-index-id bengaluru-central-test-search `
  --data-version 1 `
  --source-url "https://download.geofabrik.de/asia/india/southern-zone-260701.osm.pbf" `
  --source-timestamp "2026-07-01T20:22:00Z" `
  --created-at "2026-07-17T12:05:07Z" `
  --output out\bengaluru-central-test-search-v1.sqlite `
  --report reports\bengaluru-generation.json
```

The generator performs two streaming PBF passes. The first records only nodes within a small buffer around the approved package bounds. The second resolves named ways against that bounded node cache. It does not call Nominatim, Overpass, an online geocoder, or any online-search service.

Known generation limitation: relations are not indexed in schema v1. Named nodes and named ways are included. A way must have at least one stored node inside the exact package bounds.

The release commands pin `created_at`, so repeating the documented build does not introduce a wall-clock timestamp into the database metadata.
