# HTTP Range verification

Status: pending Release upload.

For each actual `browser_download_url`:

1. Follow HTTPS redirects while recording every hostname.
2. Request `bytes=0-16383`; require a correct `206` and `Content-Range` for resume support.
3. Request a middle and final range.
4. Build a controlled partial file and resume from its exact length.
5. Verify final byte size and SHA-256 against `PACKAGE-MANIFEST.md`.
6. Repeat with the Android downloader.

If the server answers a Range request with `200`, the safe fallback is to delete the partial and perform a complete download from byte zero. Appending a `200` response to a partial is forbidden. Size, PMTiles validation and SHA-256 remain mandatory.

Observed redirect hosts and results will be recorded here only after the draft Release exists.
