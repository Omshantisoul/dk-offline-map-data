# Phase 7 search-index Release checklist

Release tag: `phase7-search-indexes-v1`

Assets:

- `florence-test-search-v1.sqlite`
- `bengaluru-central-test-search-v1.sqlite`

Completed verification:

- [x] source byte size, checksum and PBF header metadata verified;
- [x] normalization, schema, integrity, foreign-key, bounds and golden-query tests passed;
- [x] category/place/name/token counts recorded;
- [x] local asset byte sizes and SHA-256 values recorded;
- [x] binaries uploaded as Release assets, not normal Git history;
- [x] GitHub full-download sizes and SHA-256 values match local originals;
- [x] canonical URLs and redirect hosts verified;
- [x] start and middle byte ranges returned correct `206` responses and matching bytes;
- [x] safe full-file fallback completed with exact SHA-256 match;
- [x] catalog URL, size and SHA-256 added only after verification.

Detailed network evidence is recorded in `documentation/PHASE7-HOSTING-VERIFICATION.md`.
