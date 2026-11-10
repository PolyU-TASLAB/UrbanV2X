"""Original seven camera JPEGs, matched by header time; no point overlays or labels."""
from pathlib import Path
import json,subprocess
import numpy as np,cv2
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores,get_typestore
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/previews';SOURCE=Path('/media/quintinumi/data/bag/UrbanV2Xplus/2026-8-13/honda/2026-08-13-16-01-23_0.bag');store=get_typestore(Stores.ROS1_NOETIC);rows={k:[] for k in range(7)}
with Reader(SOURCE) as reader:
 start=reader.start_time/1e9+245;end=start+6
 connections=[c for c in reader.connections if c.topic.startswith('/hikcamera/image_') and c.topic.endswith('/compressed')]
 for c,t,raw in reader.messages(connections=connections,start=int((start-.15)*1e9),stop=int((end+.15)*1e9)):
  m=store.deserialize_ros1(raw,c.msgtype);k=int(c.topic.split('image_')[1][0]);stamp=m.header.stamp.sec+m.header.stamp.nanosec/1e9;rows[k].append((stamp,m.data.tobytes()))
print('loaded',[(k,len(v)) for k,v in rows.items()],flush=True)
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','960x380','-r','6','-i','-','-an','-c:v','libx264','-crf','27','-maxrate','800k','-bufsize','1600k','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'surround.mp4')],stdin=subprocess.PIPE);times=[]
for t in np.arange(start+.1,end-.1,1/6):
 im=np.zeros((380,960,3),np.uint8);actual={}
 for k,(x,y) in {3:(0,0),2:(240,0),1:(480,0),4:(720,0),0:(120,190),6:(360,190),5:(600,190)}.items():
  stamp,b=min(rows[k],key=lambda r:abs(r[0]-t));assert abs(stamp-t)<.08,(k,stamp-t);image=cv2.imdecode(np.frombuffer(b,np.uint8),cv2.IMREAD_COLOR);im[y:y+190,x:x+240]=cv2.resize(image,(240,190));actual[k]=stamp
 if not times:cv2.imwrite(str(OUT/'surround.jpg'),im)
 times.append(actual);proc.stdin.write(im.tobytes())
proc.stdin.close();assert proc.wait()==0
(OUT/'surround-source.json').write_text(json.dumps(dict(source=str(SOURCE),offset_s=245,layout=[[3,2,1,4],[0,6,5]],max_header_delta_s=.08,frames=times),indent=2));print('surround written')
