# Release checklist

Release tag: `phase6-test-maps-v1`

Assets:

- `florence-test-v1.pmtiles`
- `bengaluru-central-test-v1.pmtiles`
- `monaco-test-v1.pmtiles`

Before publishing:

- compare each uploaded size and GitHub digest with `PACKAGE-MANIFEST.md`;
- verify all direct asset URLs and redirect hosts;
- run header, middle, end and resume Range tests;
- run a full download and SHA-256 verification;
- replace every `downloadUrl: null` only with its verified live URL;
- change package and catalog `hostingStatus` to `verified_live`;
- increment `catalogVersion` and update `generatedAt`;
- validate the final JSON against `schema-v1.json`.
