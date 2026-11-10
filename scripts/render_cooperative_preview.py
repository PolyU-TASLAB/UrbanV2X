"""Small silent preview from consecutive experimental point clouds and original boxes."""
from pathlib import Path
import zipfile,json,subprocess
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/previews';z=zipfile.ZipFile(ROOT.parent/'Urban-V2X_dropbox/extension/results/cooperative_perception/UrbanV2X_BEVFusion_EKEO1-6_LiDAR.zip');prefix='UrbanV2X_BEVFusion_EKEO1-6_LiDAR/data/EKEO1/'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','800x450','-r','6','-i','-','-an','-c:v','libx264','-crf','27','-maxrate','650k','-bufsize','1300k','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'cooperative.mp4')],stdin=subprocess.PIPE)
B=np.array([[.94,-.342,0],[.22,.60,.77]])
def project(q):
 q=q-np.array([12,0,0]);p=q@B.T;return np.round(p*np.array([5,-5])+[400,285]).astype(int)
for k in range(10,46):
 im=np.full((450,800,3),(38,27,9),np.uint8)
 for sensor,color in [('I',(90,182,239)),('V',(223,212,82))]:
  q=np.frombuffer(z.read(prefix+f'points/{sensor}/{k:05d}.bin'),dtype='<f4').reshape(-1,4)[:,:3];q=q[np.isfinite(q).all(axis=1)];q=q[(abs(q[:,0])<75)&(abs(q[:,1])<50)&(q[:,2]>-3)&(q[:,2]<22)][::2];uv=project(q);ok=(uv[:,0]>1)&(uv[:,0]<799)&(uv[:,1]>1)&(uv[:,1]<449);uv=uv[ok];im[uv[:,1],uv[:,0]]=color
 for b in json.loads(z.read(prefix+f'labels/{k:05d}.json'))['boxes']:
  q=np.array([[x,y,h] for h in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]])*[b['length'],b['width'],b['height']];c,s=np.cos(b['yaw']),np.sin(b['yaw']);q=q@np.array([[c,s,0],[-s,c,0],[0,0,1]])+[b['x'],b['y'],b['z']];uv=project(q)
  for i in range(8):
   for j in range(i+1,8):
    if bin(i^j).count('1')==1:cv2.line(im,tuple(uv[i]),tuple(uv[j]),(173,246,161),1,cv2.LINE_AA)
 if k==10:cv2.imwrite(str(OUT/'cooperative.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,88])
 proc.stdin.write(im.tobytes())
proc.stdin.close();assert proc.wait()==0
print((OUT/'cooperative.mp4').stat().st_size)
