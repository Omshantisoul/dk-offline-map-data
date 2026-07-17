# Phase 6 test-package manifest

| Asset | Bytes | SHA-256 | Bounds (W,S,E,N) | Zoom | Tile/schema | Validation |
|---|---:|---|---|---|---|---|
| `florence-test-v1.pmtiles` | 6,601,156 | `7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a` | `11.221144,43.745121,11.287543,43.789306` | 0-15 | PMTiles v3, gzip MVT, Protomaps Basemap | `pmtiles verify` passed |
| `bengaluru-central-test-v1.pmtiles` | 10,154,053 | `1c6a0fe5de649181ea98b70b27a54d058ec8aae32a80a38c6103bb235580f6fd` | `77.55,12.92,77.68,13.05` | 0-14 | PMTiles v3, gzip MVT, OpenMapTiles 3.16.0 | `pmtiles verify` passed |
| `monaco-test-v1.pmtiles` | 376,528 | `aa85dbaedde977b0a57353b7d48fbb63037ecb7b9b3b43347f6386eea9136338` | `7.409,43.7239999,7.44,43.752` | 0-14 | PMTiles v3, gzip MVT, OpenMapTiles 3.16.0 | `pmtiles verify` passed |

The OpenMapTiles packages include layers such as `boundary`, `building`, `landcover`, `landuse`, `place`, `transportation`, and `water`. Florence retains its original Protomaps layer schema.

The Release tagged `phase6-test-maps-v1` is live and independently verified. Canonical URLs are recorded in `catalog/catalog.json`; Range and full-file verification results are recorded in `documentation/HTTP-RANGE-VERIFICATION.md`.
