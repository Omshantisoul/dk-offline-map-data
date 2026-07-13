# Reproducible package generation

## Pinned tools

- Planetiler `v0.10.2`, SHA-256 `f310bd0413e2e4512b27f4046d418664e8e1d3bf31603c2a70e23de06c167e4d`
- go-pmtiles `v1.31.0` Windows x86-64 archive, SHA-256 `bb2a0c52d54f560cc2ce4fe47289e082599363f5ff3ee49c76ffc33388340734`

Planetiler generated OpenMapTiles schema `3.16.0`, gzip-compressed MVT in PMTiles v3. Supporting Natural Earth, lake-centerline and water-polygon resources were downloaded by Planetiler's pinned profile. Their features may appear at low zoom; attribution embedded by the profile remains authoritative.

## Bengaluru Central

Input: `southern-zone-260701.osm.pbf` from Geofabrik, verified MD5 `a4b4bd58527414b456dfccb96548e3e5`.

```powershell
java -Xmx6g -jar planetiler-0.10.2.jar `
  --osm-path=southern-zone-260701.osm.pbf `
  --output=bengaluru-central-test-v1.pmtiles `
  --bounds=77.55,12.92,77.68,13.05 `
  --minzoom=0 --maxzoom=14 --force
```

## Monaco

Input: `monaco-260701.osm.pbf` from Geofabrik, verified MD5 `a12c43f1b8b03f981d1e85cee89a884b`.

```powershell
java -Xmx4g -jar planetiler-0.10.2.jar `
  --osm-path=monaco-260701.osm.pbf `
  --output=monaco-test-v1.pmtiles `
  --bounds=7.409,43.724,7.440,43.752 `
  --minzoom=0 --maxzoom=14 --force
```

## Florence

Florence was not regenerated. The accepted Phase 5 file was copied only after its exact byte count and SHA-256 matched the pinned upstream fixture.

All final files passed `pmtiles verify` with go-pmtiles `v1.31.0`; header and metadata were then inspected using `pmtiles show --header-json` and `pmtiles show --metadata`.
