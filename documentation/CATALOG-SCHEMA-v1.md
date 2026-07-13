# Catalog schema v1

The catalog is metadata only. It cannot supply executable code or downloadable style expressions.

Before acceptance a client must validate schema version, unique IDs, parent existence, hierarchy acyclicity, safe IDs, bounds, zooms, compatibility identifiers, HTTPS URLs, host allowlists, sizes and hashes. Unknown critical extensions reject the complete remote catalog and preserve the last-known-good catalog.

`downloadUrl` is nullable only while `hostingStatus` is `pending_release_upload`. Such packages are documentation records and must not expose Download/Open actions. A live catalog requires an HTTPS URL and `verified_live` after Release size, hash, redirects and Range behavior have been checked.

Region names and relationships are reviewed catalog metadata, not political claims embedded in Android code. Every package here has `productionReady: false`.
