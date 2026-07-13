# HTTP Range verification

Status: verified 2026-07-13 against the published `phase6-test-maps-v1` Release.

For each actual `browser_download_url`:

1. Follow HTTPS redirects while recording every hostname.
2. Request `bytes=0-16383`; require a correct `206` and `Content-Range` for resume support.
3. Request a middle and final range.
4. Build a controlled partial file and resume from its exact length.
5. Verify final byte size and SHA-256 against `PACKAGE-MANIFEST.md`.
6. Repeat with the Android downloader.

If the server answers a Range request with `200`, the safe fallback is to delete the partial and perform a complete download from byte zero. Appending a `200` response to a partial is forbidden. Size, PMTiles validation and SHA-256 remain mandatory.

Observed redirect chain for all three assets:

`github.com` -> `release-assets.githubusercontent.com`

Results:

| Asset | Range response | Content-Range total | Full bytes | Full SHA-256 |
|---|---|---:|---:|---|
| `florence-test-v1.pmtiles` | `206`, 16,384 bytes | 6,601,156 | 6,601,156 | `7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a` |
| `bengaluru-central-test-v1.pmtiles` | `206`, 16,384 bytes | 10,154,053 | 10,154,053 | `1c6a0fe5de649181ea98b70b27a54d058ec8aae32a80a38c6103bb235580f6fd` |
| `monaco-test-v1.pmtiles` | `206`, 16,384 bytes | 376,528 | 376,528 | `aa85dbaedde977b0a57353b7d48fbb63037ecb7b9b3b43347f6386eea9136338` |

Every server response included `Accept-Ranges: bytes` and a correct `Content-Range`. Safe full-file fallback remains required in the client in case GitHub behavior changes later.
