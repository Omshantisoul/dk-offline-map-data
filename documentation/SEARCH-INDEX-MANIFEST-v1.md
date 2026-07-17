# Phase 7 search-index manifest v1

Release tag: `phase7-search-indexes-v1`

Hosting status: verified live on 2026-07-17.

## Florence

- asset: `florence-test-search-v1.sqlite`
- byte size: `3,411,968`
- SHA-256: `7c8279c7425720e1ff8c1061275d5e0056ccb37d19c69d6a6278d519f7de1780`
- URL: `https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase7-search-indexes-v1/florence-test-search-v1.sqlite`
- places: `6,210`
- names: `7,122`
- search tokens: `20,673`
- categories: atm 9, bank 79, bus station 2, education 114, food 1,242, fuel 29, health 87, hospital 7, landmark 350, lodging 350, police 22, railway station 4, road 3,842, settlement 20, vehicle 53

## Bengaluru Central

- asset: `bengaluru-central-test-search-v1.sqlite`
- byte size: `18,100,224`
- SHA-256: `a16a41ebcf78c7f57c7531aae630aa82d99bb5a04678835ab7218e9246964b37`
- URL: `https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase7-search-indexes-v1/bengaluru-central-test-search-v1.sqlite`
- places: `20,461`
- names: `41,217`
- search tokens: `113,445`
- categories: atm 349, bank 822, bus station 30, education 811, fire station 10, food 3,128, fuel 170, health 969, hospital 518, landmark 1,057, lodging 502, police 87, railway station 37, road 11,432, settlement 484, vehicle 55

## Validation state

Both assets pass SQLite integrity and quick checks, foreign-key checks, schema/application ID validation, package-bounds validation, normalization unit tests, and package-specific golden-query tests. Uploaded bytes were independently downloaded and matched to the local originals by size and SHA-256. Start and middle HTTP Range requests returned correct `206` responses and byte-identical content.

## Known limitations

- Developer-test areas only; these are not production India or world search indexes.
- Named OSM nodes and ways are indexed; relations are not indexed in schema v1.
- No house-number geocoding, online fallback, routing, or navigation data is included.
- Search quality depends on the names and tags present in the pinned OpenStreetMap extracts.
