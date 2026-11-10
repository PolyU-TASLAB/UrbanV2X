from pathlib import Path
import subprocess,json,sys
OUT=Path(__file__).resolve().parents[1]/'assets/previews'
for name in (sys.argv[1:] or ['platform','multi-lidar','lidar-camera','cooperative','positioning','surround','reconstruction','reconstruction-vggt','carla']):
 src=OUT/(name+'-raw.mp4' if name=='positioning' else name+'.mp4');duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(src)]));fade=.8 if duration>=5 else .6
 vf=f'[0:v]fps=10,split[a][b];[a]trim=start={fade},setpts=PTS-STARTPTS[main];[b]trim=end={fade},setpts=PTS-STARTPTS[head];[main][head]xfade=transition=fade:duration={fade}:offset={duration-2*fade},format=yuv420p[v]'
 dst=OUT/f'{name}-loop.mp4';subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-filter_complex',vf,'-map','[v]','-an','-c:v','libx264','-threads','2','-crf','27','-maxrate','700k','-bufsize','1400k','-movflags','+faststart',str(dst)],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(dst),'-frames:v','1','-q:v','4',str(OUT/f'{name}.jpg')],check=True);print(name,round(dst.stat().st_size/1024),'KiB',flush=True)
