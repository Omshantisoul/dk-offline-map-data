# Phase 7 hosting verification

Verified on 2026-07-17 against Release `phase7-search-indexes-v1`.

## Redirect and host results

Both canonical download URLs returned `302 Found` from `github.com` and redirected to a signed URL on `release-assets.githubusercontent.com`. The signed URL is temporary and is not stored in the catalog. The final response was served by Azure Blob infrastructure through GitHub's release-asset host.

Observed HTTPS host allowlist:

- `github.com`
- `release-assets.githubusercontent.com`

## Full-file verification

| Asset | Response | Bytes | SHA-256 | Local match |
|---|---:|---:|---|---|
| `florence-test-search-v1.sqlite` | `200 OK` | 3,411,968 | `7c8279c7425720e1ff8c1061275d5e0056ccb37d19c69d6a6278d519f7de1780` | yes |
| `bengaluru-central-test-search-v1.sqlite` | `200 OK` | 18,100,224 | `a16a41ebcf78c7f57c7531aae630aa82d99bb5a04678835ab7218e9246964b37` | yes |

## HTTP Range verification

For each asset, `Range: bytes=0-16383` and `Range: bytes=65536-81919` returned `206 Partial Content`, `Content-Length: 16384`, `Accept-Ranges: bytes`, and the correct total in `Content-Range`. Both returned byte blocks matched the same offsets in the verified full download.

## Safe full-file fallback

Range support is currently reliable, but is not required for search-index installation. If a future server ignores a Range request and returns `200`, the client must discard any partial file and perform a fresh full-file download from byte zero. It must never append a `200` response to a partial file. Size, SHA-256, SQLite integrity, schema, metadata and bounds validation remain mandatory before atomic installation.
