"""Matched GT, RAWX, NAV-SAT and UWB timeline; no invented satellite visibility."""
from pathlib import Path
import json,struct,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];u=json.loads((ROOT/'assets/data/uwb.json').read_text());b=Path('/media/quintinumi/data/bag/UrbanV2Xplus/2026-8-13/honda/2026_8_13_14_53_17.ubx').read_bytes();i=0;nav={};raw={};week=2431;leap=18
lo=374500;hi=374810
while i<len(b)-8:
 i=b.find(b'\xb5\x62',i)
 if i<0:break
 cl,mid,n=struct.unpack_from('<BBH',b,i+2);p=b[i+6:i+6+n];packet=b[i+2:i+6+n];check=b[i+6+n:i+8+n];i+=n+8
 if (cl,mid) not in [(1,53),(2,21)]:continue
 a=c=0
 for byte in packet:a=(a+byte)&255;c=(c+a)&255
 if check!=bytes([a,c]):continue
 if mid==53:
  tow=struct.unpack_from('<I',p)[0]/1000
  if not lo<=tow<=hi:continue
  sats=[]
  for j in range(p[5]):
   gn,sv,cno,el,az,res,flags=struct.unpack_from('<BBBbhhI',p,8+j*12);eph=bool(flags&(1<<11));orbit=(flags>>8)&7;quality=flags&7
   if not(10<=el<=90 and 0<=az<=360):continue
   if cno>0 or eph:
    sats.append(dict(id=f'{gn}-{sv}',gnss=gn,sv=sv,az=az,el=el,cno=cno,eph=eph,orbit_source=orbit,quality=quality,nlos_candidate=eph and cno==0 and quality<=1))
  nav[round(tow)]=sats
 else:
  tow,week,leap,num=struct.unpack_from('<dHbB',p,0)
  if not lo<=tow<=hi:continue
  rr={}
  for j in range(num):
   off=16+j*32;pr=struct.unpack_from('<d',p,off)[0];gn,sv=p[off+20:off+22];valid=bool(p[off+30]&1)
   if valid and math.isfinite(pr) and 1e6<pr<5e7:rr.setdefault(f'{gn}-{sv}',round(pr,3))
  raw[round(tow)]=rr
base=315964800+week*604800-leap;frames=[]
for tow,sats in sorted(nav.items()):
 utc=base+tow;dt=utc-u['start_unix_s']
 if not 0<=dt<=u['duration_s']:continue
 k=int(np.argmin([abs(r[0]-dt) for r in u['samples']]));nearest=u['samples'][k];ranges=nearest[1:] if abs(nearest[0]-dt)<.55 else [None]*len(u['ids'])
 for sat in sats:sat['pseudorange_m']=raw.get(tow,{}).get(sat['id'])
 frames.append(dict(utc=utc,t=round(dt,3),position=u['positions'][k][:2],satellites=sats,ranges=ranges))
result=dict(frames=frames,anchor=u['mapped_node'],anchors=u['mapped_nodes'],uwb_ids=u['ids'],source='2026-08-13 Honda UBX + bag + honda_2 RTK/INS',red_rule='NAV-SAT ephAvail = 1, elevation >= 10 deg, C/N0 = 0 and qualityInd <= 1. NLOS candidate, not verified blockage.',satellite_radius='display only; positions use receiver-reported azimuth/elevation',documentation='https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.51_InterfaceDescription_UBXDOC-963802114-13124.pdf')
(ROOT/'assets/data/positioning-timeline.json').write_text(json.dumps(result,separators=(',',':')))
print('frames',len(frames),'red counts',min(sum(s['nlos_candidate'] for s in f['satellites']) for f in frames),max(sum(s['nlos_candidate'] for s in f['satellites']) for f in frames))
