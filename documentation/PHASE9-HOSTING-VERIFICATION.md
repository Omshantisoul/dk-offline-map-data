# Phase 9 routing asset hosting verification

Approval Gate 1 live verification completed by GitHub Actions.

- Workflow run: https://github.com/Omshantisoul/dk-offline-map-data/actions/runs/29687626256
- Result: success
- Artifact: `phase9-routing-verification`
- BRouter package: `brouter-1.7.10.zip`, 6,724,983 bytes, SHA-256 `023FEC3BA997758E8CD7AB9E1BAE52E962AF3F00B57683E3DE86B84FFAD01532`

## Verified assets

| Region | Release asset | Size | SHA-256 | Final host | Range | Route |
|---|---|---:|---|---|---|---|
| Florence | `florence-test-routing-v1.zip` | 37,186,120 | `3DA87C3DAA1775BB4B3A69AB4E80D03FAD07BD729F465244D88B5767F58076ED` | `release-assets.githubusercontent.com` | start + middle HTTP 206 | PASS |
| Bengaluru | `bengaluru-central-test-routing-v1.zip` | 48,550,828 | `4EBCC9BB64D0253702D96DD231475C96168BDC3DDAB7F6BD1D1B36F3D51F892E` | `release-assets.githubusercontent.com` | start + middle HTTP 206 | PASS |

Canonical URLs:

- https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase9-routing-data-v1/florence-test-routing-v1.zip
- https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase9-routing-data-v1/bengaluru-central-test-routing-v1.zip

Both ZIPs passed full-file size/SHA-256 checks, ZIP integrity, safe extraction, manifest validation and nested rd5 hash validation. The workflow also ran one offline in-process BRouter golden route per region. A complete verified download is the safe fallback when HTTP Range is unavailable.

## Catalog routing metadata

Catalog version 4 adds a `routing` object only to Florence and Bengaluru. Each object records the verified Release URL, archive size/SHA-256, BRouter 1.7.10 and immutable commit `4d2639af77ea5ed9c30d3e400764eb6f9e8522da`, schema version 1, both supported profiles, rd5 segment metadata, source URL/hash, observed source bounds, attribution and `elevationIncluded: false`. Monaco intentionally has no routing metadata.

The rd5 files are BRouter 5x5-degree grid segments populated by the approved extracts. Their observed bounds are limited to the source extracts and do not claim complete grid coverage.

## Provenance and licensing

Generation used the pinned BRouter map-creator toolchain (OsmFastCutter, PosUnifier and WayLinker; Java 21; Gradle 9.4.1). Archives include BRouter MIT licensing, profile notices, OpenStreetMap ODbL source notice and attribution. Source and segment hashes are recorded in the archive manifests and local generation evidence.
