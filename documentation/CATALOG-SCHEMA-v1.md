# Catalog schema v1

The catalog is metadata only. It cannot supply executable code or downloadable style expressions.

Before acceptance a client must validate schema version, unique IDs, parent existence, hierarchy acyclicity, safe IDs, bounds, zooms, compatibility identifiers, HTTPS URLs, host allowlists, sizes and hashes. Unknown critical extensions reject the complete remote catalog and preserve the last-known-good catalog.

`downloadUrl` is nullable only while `hostingStatus` is `pending_release_upload`. Such packages are documentation records and must not expose Download/Open actions. A live catalog requires an HTTPS URL and `verified_live` after Release size, hash, redirects and Range behavior have been checked.

Region names and relationships are reviewed catalog metadata, not political claims embedded in Android code. Every package here has `productionReady: false`.

Phase 7 searchable packages may additionally declare the complete companion-search field set: `searchIndexId`, `searchSchemaVersion`, `searchDataVersion`, `searchUrl`, `searchSizeBytes`, `searchSha256`, `searchPackageId`, `searchBounds`, `searchLanguages`, `searchFeatureClasses`, `searchDataTimestamp` and `searchAttribution`. A package with any companion-search field must provide and validate the complete set. Packages without an installed or published search index may omit the entire set; missing search metadata must never prevent the PMTiles map itself from opening.

`searchUrl` is accepted only from the reviewed HTTPS host allowlist. `searchPackageId` must equal the containing map `packageId` for the Phase 7 test assets. The downloaded SQLite file must match the declared size and SHA-256, pass SQLite/schema/metadata/bounds validation, and be atomically installed before it becomes active.
