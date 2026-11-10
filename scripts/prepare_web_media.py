"""Re-encode text-free experimental renders; never use paper figures as inputs."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]; WS=ROOT.parent
CLEAN=WS/'ws_data-flywheel/workspaces/sensor_calibration/common/runs/visual_review/20261014_oblique_round_v3/videos'
OUT=ROOT/'assets/media'; OUT.mkdir(exist_ok=True)
jobs=[
 ('platform', ROOT/'assets/gif/onboard_platform_speedX4.gif',0,8,'scale=1280:-2'),
 ('multi-lidar',CLEAN/'aug13_vehicle_lidar_oblique_clean.mp4',8,12,'scale=1280:-2'),
 ('surround-projection',CLEAN/'aug13_lidar_cam_clean.mp4',8,12,'scale=1760:-2'),
 ('front-projection',CLEAN/'aug13_lidar_cam_clean.mp4',8,12,'crop=1100:435:550:0,scale=1280:-2'),
]
manifest=[]
existing=json.loads((OUT/'provenance.json').read_text()) if (OUT/'provenance.json').exists() else []
for name,src,start,duration,vf in jobs:
 out=OUT/f'{name}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(src),'-t',str(duration),'-vf',vf,'-an','-r','15','-c:v','libx264','-threads','2','-crf','23','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-ss','1','-i',str(out),'-frames:v','1','-q:v','2',str(OUT/f'{name}.jpg')],check=True)
 manifest.append(dict(asset=f'assets/media/{name}.mp4',source=str(src.relative_to(WS)),start_s=start,duration_s=duration,filter=vf,notes='Experimental render; no embedded labels. Front projection: cam2 left, cam1 right.'))
 print(name,flush=True)
updated={m['asset'] for m in manifest}
(OUT/'provenance.json').write_text(json.dumps(manifest+[m for m in existing if m['asset'] not in updated],indent=2,ensure_ascii=False))
