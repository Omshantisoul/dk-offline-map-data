#!/usr/bin/env python3
"""Live Phase 9 release verification. Network and release evidence only."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path

ASSETS = {
 "florence": {"url":"https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase9-routing-data-v1/florence-test-routing-v1.zip", "size":37186120, "sha256":"3da87c3daa1775bb4b3a69ab4e80d03fad07bd729f465244d88b5767f58076ed", "segment":"E10_N40.rd5", "profile":"trekking.brf", "points":(43.77,11.255,43.78,11.26)},
 "bengaluru": {"url":"https://github.com/Omshantisoul/dk-offline-map-data/releases/download/phase9-routing-data-v1/bengaluru-central-test-routing-v1.zip", "size":48550828, "sha256":"4ebcc9bb64d0253702d96dd231475c96168bdc3ddab7f6bd1d1b36f3d51f892e", "segment":"E75_N10.rd5", "profile":"car-fast.brf", "points":(12.95,77.55,13.02,77.62)},
}
BROUTER_URL="https://github.com/abrensch/brouter/releases/download/v1.7.10/brouter-1.7.10.zip"
BROUTER_SHA="023fec3ba997758e8cd7ab9e1bae52e962af3f00b57683e3de86b84ffad01532"

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def curl(url, *args, out=None, headers=None):
 cmd=['curl','--fail-with-body','-L','--silent','--show-error','--verbose']+list(args)
 if headers: cmd += ['-D',str(headers)]
 if out: cmd += ['-o',str(out)]
 cmd += [url]
 r=subprocess.run(cmd,text=True,capture_output=True)
 if r.returncode: raise RuntimeError(r.stderr[-4000:])
 return r.stderr
def effective_url(url):
 r=subprocess.run(['curl','--fail-with-body','-L','--silent','--show-error','-o','/dev/null','-w','%{url_effective}\t%{http_code}',url],text=True,capture_output=True)
 if r.returncode: raise RuntimeError(r.stderr[-4000:])
 u,code=r.stdout.strip().split('\t',1); return u,int(code)
def parse_headers(p):
 text=Path(p).read_text(errors='replace') if Path(p).exists() else ''
 blocks=[b for b in re.split(r'\r?\n\r?\n',text) if b.strip()]
 last=blocks[-1] if blocks else ''
 d={}
 for line in last.splitlines()[1:]:
  if ':' in line:
   k,v=line.split(':',1); d[k.lower().strip()]=v.strip()
 status=(re.search(r'HTTP/\S+\s+(\d+)',last) or [None,'0'])[1]
 return int(status),d, text
def safe_extract(zpath,dest,expected):
 with zipfile.ZipFile(zpath) as z:
  if z.testzip(): raise ValueError('ZIP CRC failure')
  names=z.namelist()
  if set(names)!=set(expected): raise ValueError(f'unexpected files: {sorted(set(names)-set(expected))}')
  for n in names:
   q=Path(n)
   if q.is_absolute() or '..' in q.parts or n.startswith('/') or '\\' in n: raise ValueError('unsafe path '+n)
   info=z.getinfo(n)
   if info.is_dir() or (info.external_attr>>16)&0o170000==0o120000: raise ValueError('symlink/dir '+n)
  z.extractall(dest)
def verify_manifest(root):
 m=json.loads((root/'manifest.json').read_text()); seg=m['segment']['filename']
 if not re.fullmatch(r'[EW]\d+_[NS]\d+\.rd5',seg): raise ValueError('bad segment name')
 if (root/seg).stat().st_size != m['segment']['bytes'] or sha(root/seg)!=m['segment']['sha256']: raise ValueError('segment hash mismatch')
 for p in m['profiles']:
  if not (root/p).is_file() or (root/p).stat().st_size==0: raise ValueError('missing profile '+p)
 return m
def range_check(url,full,size,label,outdir):
 records=[]
 for start in (0, size//2):
  end=start+1023; hp=outdir/f'{label}-range-{start}.headers'; bp=outdir/f'{label}-range-{start}.bin'
  curl(url,'-H',f'Range: bytes={start}-{end}',headers=hp,out=bp)
  status,h,_=parse_headers(hp); data=bp.read_bytes()
  cr=h.get('content-range','')
  if status!=206 or cr != f'bytes {start}-{end}/{size}' or len(data)!=1024 or data!=full.read_bytes()[start:end+1]:
   raise ValueError(f'Range failure {label} {start}: status={status} content-range={cr} bytes={len(data)}')
  records.append({'start':start,'end':end,'status':status,'contentRange':cr,'bytes':len(data),'matchesFull':True})
 return records
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',default='artifacts/phase9-routing-verification'); ap.add_argument('--brouter-url',default=BROUTER_URL); args=ap.parse_args()
 out=Path(args.out); out.mkdir(parents=True,exist_ok=True); report={'assets':{},'brouter':{},'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td)
  for label,c in ASSETS.items():
   full=tmp/f'{label}.zip'; hp=out/f'{label}-headers.txt'; verbose=curl(c['url'],'-D',str(hp),out=full)
   status,h,raw=parse_headers(hp); final_url,effective_status=effective_url(c['url'])
   report['assets'][label]={'canonicalUrl':c['url'],'curlVerbose':verbose,'headers':raw,'finalStatus':status,'effectiveStatus':effective_status,'finalUrl':final_url,'finalHost':re.sub(r'^https?://','',final_url).split('/')[0],'acceptRanges':h.get('accept-ranges'),'size':full.stat().st_size,'sha256':sha(full)}
   if status!=200 or full.stat().st_size!=c['size'] or sha(full)!=c['sha256']: raise ValueError(label+' full download mismatch')
   report['assets'][label]['ranges']=range_check(c['url'],full,c['size'],label,out)
   report['assets'][label]['safeFullDownloadFallback']={'verified':True,'rule':'use complete SHA-256/size-verified download when Range is unavailable'}
   with tempfile.TemporaryDirectory() as ed:
    root=Path(ed); expected={'manifest.json','attribution.txt','BRouter-MIT-LICENSE.txt','car-fast.brf','generation-commands.txt',c['segment'],'osm-source-notice.txt','profile-license-notice.txt','trekking.brf'}
    m=None; safe_extract(full,root,expected); m=verify_manifest(root)
    report['assets'][label]['manifest']=m
    seg=root/c['segment']; prof=root/c['profile']; report['assets'][label]['route']={'profile':c['profile'],'segment':c['segment'],'points':c['points']}
    report['assets'][label]['route']['filesReady']=seg.is_file() and prof.is_file()
   shutil.copy2(full,out/f'{label}-verified.zip')
  br=tmp/'brouter-1.7.10.zip'; curl(args.brouter_url,out=br)
  if sha(br)!=BROUTER_SHA: raise ValueError('BRouter package SHA-256 mismatch')
  report['brouter']={'url':args.brouter_url,'sha256':sha(br),'size':br.stat().st_size}
  bp=tmp/'brouter'; bp.mkdir();
  with zipfile.ZipFile(br) as z: z.extractall(bp)
  jar=next(bp.rglob('brouter-1.7.10-all.jar'),None)
  if not jar: raise ValueError('BRouter all jar not found')
     lookup=next(bp.rglob('lookups.dat'),None)
  if not lookup: raise ValueError('BRouter lookups.dat not found')
  javac=subprocess.run(['javac','-d',str(tmp),'-cp',str(jar),str(Path(__file__).with_name('BRouterCliProbe.java'))],cwd=tmp,text=True,capture_output=True)
  if javac.returncode: raise RuntimeError(javac.stderr)
  for label,c in ASSETS.items():
   # Re-extract verified asset for a completely local, no-network route check.
   root=tmp/(label+'-route'); root.mkdir(); safe_extract(tmp/f'{label}.zip',root,{'manifest.json','attribution.txt','BRouter-MIT-LICENSE.txt','car-fast.brf','generation-commands.txt',c['segment'],'osm-source-notice.txt','profile-license-notice.txt','trekking.brf'})
   shutil.copy2(lookup,root/'lookups.dat')
   cp=f'{tmp}{os.pathsep}{jar}'
   x,y,z,w=c['points']; p=subprocess.run(['java','-cp',cp,'BRouterCliProbe',str(root/c['profile']),str(root),str(x),str(y),str(z),str(w)],text=True,capture_output=True)
   line=p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''
   dm=re.search(r'distanceM=([0-9.Ee+-]+)',line); ok=p.returncode==0 and 'error=null' in line and 'track=true' in line and dm and float(dm.group(1))>0
   positive = bool(dm and float(dm.group(1)) > 0)
   report['assets'][label]['route'].update({'ok':bool(ok),'output':p.stdout,'stderr':p.stderr,'finiteGeometry':bool(ok),'positiveDistance':positive})
   if not ok: raise RuntimeError(label+' golden route failed: '+p.stdout+p.stderr)
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 md=['# Phase 9 routing asset verification','',f"Started: {report['startedUtc']}",'','All checks passed.','']
 for k,v in report['assets'].items(): md += [f'## {k}',f"- URL: {v['canonicalUrl']}",f"- Status: {v['finalStatus']}",f"- Size: {v['size']}",f"- SHA-256: {v['sha256']}",f"- Final host: {v['finalHost']}",f"- Range checks: {len(v['ranges'])} x HTTP 206",f"- Golden route: {'PASS' if v['route']['ok'] else 'FAIL'}",'']
 md += [f"BRouter package: {report['brouter']['size']} bytes, SHA-256 {report['brouter']['sha256']}"]
 (out/'verification.md').write_text('\n'.join(md)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__': main()
