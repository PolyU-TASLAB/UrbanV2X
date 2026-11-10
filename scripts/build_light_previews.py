from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1];WS=ROOT.parent;OUT=ROOT/'assets/previews';OUT.mkdir(exist_ok=True)
jobs=[('platform',ROOT/'assets/gif/onboard_platform_speedX4.gif',0,6,'scale=800:-2'),('multi-lidar',WS/'ws_data-flywheel/workspaces/sensor_calibration/common/runs/visual_review/20261014_oblique_round_v3/videos/aug13_vehicle_lidar_oblique_clean.mp4',8,6,'scale=800:-2'),('lidar-camera',WS/'ws_data-flywheel/workspaces/sensor_calibration/lidar_cam/runs/multicamera_video/20260915T182812Z_small_60s/videos/七相机点云投影_一分钟_大点.mp4',18,6,'[0:v]split[t][b];[t]crop=3520:658:0:38[top];[b]crop=3520:658:0:734[bottom];[top][bottom]vstack,scale=960:-2,fps=10[v]'),('carla',WS/'Urban-V2X_dropbox/extension/video/carla_hkstp_showcase.mp4',8,4,'crop=956:540:964:64,scale=640:-2'),('reconstruction',WS/'Urban-V2X_dropbox/extension/video/重建/reconstruction.mp4',8,4,'crop=800:450:96:94,scale=640:-2')]
manifest=[]
for name,src,start,duration,filter in jobs:
 dst=OUT/f'{name}.mp4'
 vf=['-filter_complex',filter,'-map','[v]'] if name=='lidar-camera' else ['-vf',filter+',fps=10']
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(src),'-t',str(duration),*vf,'-an','-c:v','libx264','-threads','2','-preset','fast','-crf','28','-maxrate','700k','-bufsize','1400k','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-ss','1','-i',str(dst),'-frames:v','1','-q:v','4',str(OUT/f'{name}.jpg')],check=True)
 manifest.append(dict(asset=dst.name,source=str(src.relative_to(WS)),start_s=start,duration_s=duration,filter=filter,size_bytes=dst.stat().st_size));print(name,dst.stat().st_size,flush=True)
existing=json.loads((OUT/'sources.json').read_text()) if (OUT/'sources.json').exists() else []
updated={r['asset'] for r in manifest}
(OUT/'sources.json').write_text(json.dumps(manifest+[r for r in existing if r['asset'] not in updated],indent=2,ensure_ascii=False))
