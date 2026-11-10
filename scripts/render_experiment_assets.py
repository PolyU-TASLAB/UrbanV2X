"""Generate label-free web assets directly from recorded experimental data."""
from pathlib import Path
import json,zipfile,struct,math,csv,io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection,Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]; WS=ROOT.parent; OUT=ROOT/'assets/media'; DATA=ROOT/'assets/data'
# Render original aligned point clouds and original reference boxes. No paper image input.
z=zipfile.ZipFile(WS/'Urban-V2X_dropbox/extension/results/cooperative_perception/UrbanV2X_BEVFusion_EKEO1-6_LiDAR.zip');prefix='UrbanV2X_BEVFusion_EKEO1-6_LiDAR/data/EKEO1/'
fig=plt.figure(figsize=(12.8,7.2),facecolor='#091b26');ax=fig.add_axes([0,0,1,1],projection='3d',facecolor='#091b26')
for mode,col in [('I','#efb65a'),('V','#52d4df')]:
 p=np.frombuffer(z.read(prefix+f'points/{mode}/00010.bin'),dtype='<f4').reshape(-1,4)[:,:3];p=p[np.isfinite(p).all(axis=1)];p=p[(p[:,0]>-45)&(p[:,0]<70)&(abs(p[:,1])<38)&(p[:,2]>-3)&(p[:,2]<18)][::2];ax.scatter(*p.T,s=.35,c=col,alpha=.7,linewidths=0,rasterized=True)
labels=json.loads(z.read(prefix+'labels/00010.json'))
for b in labels['boxes']:
 corners=np.array([[x,y,zz] for zz in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]])*np.array([b['length'],b['width'],b['height']]);c,s=np.cos(b['yaw']),np.sin(b['yaw']);corners=corners@np.array([[c,s,0],[-s,c,0],[0,0,1]])+np.array([b['x'],b['y'],b['z']]);edges=[(i,j) for i in range(8) for j in range(i+1,8) if bin(i^j).count('1')==1];ax.add_collection3d(Line3DCollection([[corners[i],corners[j]] for i,j in edges],colors='#a1f6ad',linewidths=1.2))
ax.set(xlim=(-45,70),ylim=(-38,38),zlim=(-4,25));ax.set_box_aspect((115,76,29));ax.view_init(42,-78);ax.dist=7;ax.set_axis_off();fig.savefig(OUT/'cooperative-labels.jpg',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)
# Decode checked UBX packets. RXM-RAWX: recorded pseudorange; NAV-SAT: receiver satellite azimuth/elevation.
raw=Path('/media/quintinumi/data/bag/UrbanV2Xplus/2026-8-13/honda/2026_8_13_14_53_17.ubx');buf=raw.read_bytes();i=0;epochs=[];sky={};target=374791.0
while i<len(buf)-8:
 i=buf.find(b'\xb5\x62',i)
 if i<0:break
 cl,mid,n=struct.unpack_from('<BBH',buf,i+2);p=buf[i+6:i+6+n];packet=buf[i+2:i+6+n];a=b=0
 for byte in packet:a=(a+byte)&255;b=(b+a)&255
 ok=buf[i+6+n:i+8+n]==bytes([a,b]);i+=n+8
 if not ok:continue
 if (cl,mid)==(2,21):
  tow,week,leap,num=struct.unpack_from('<dHbB',p,0)
  if abs(tow-target)>60:continue
  rows=[]
  for j in range(num):
   off=16+j*32;pr,cp,dop=struct.unpack_from('<ddf',p,off);gn,sv,sig,freq=struct.unpack_from('<BBBB',p,off+20);cno=p[off+26];trk=p[off+30]
   if trk&1 and math.isfinite(pr) and 1e6<pr<5e7:rows.append(dict(gnss=gn,sv=sv,signal=sig,pseudorange_m=round(pr,3),cno=cno))
  epochs.append(dict(tow=tow,week=week,utc=315964800+week*604800+tow-leap,measurements=rows))
 if (cl,mid)==(1,53):
  tow=struct.unpack_from('<I',p)[0]/1000
  if abs(tow-target)<1:
   for j in range(p[5]):
    gn,sv,cno,el,az,res,flags=struct.unpack_from('<BBBbhhI',p,8+j*12)
    if el>5:sky[f'{gn}-{sv}']=dict(gnss=gn,sv=sv,elevation=el,azimuth=az,cno=cno)
epoch=min(epochs,key=lambda e:abs(e['tow']-target));track=np.load(WS/'ws_urbanv2x_ijrr/metadata/trajectory_maps/honda_2.npz');ts=track['time_ns']/1e9;idx=int(np.argmin(abs(ts-epoch['utc'])));lat=float(track['latitude'][idx]);lon=float(track['longitude'][idx]);m=(ts>=epoch['utc']-45)&(ts<=epoch['utc']);trajectory=np.column_stack([track['longitude'][m][::10],track['latitude'][m][::10],track['altitude'][m][::10]]).tolist()
result=dict(source=str(raw),epoch=epoch,satellites=list(sky.values()),epochs=epochs,vehicle=dict(latitude=lat,longitude=lon,altitude=float(track['altitude'][idx])),trajectory=trajectory,gt_source='metadata/trajectory_maps/honda_2.npz',gt_time_error_s=float(ts[idx]-epoch['utc']))
(DATA/'gnss.json').write_text(json.dumps(result,separators=(',',':')))
print('Cooperative and GNSS assets written:',len(epochs),'epochs',len(sky),'satellites')
