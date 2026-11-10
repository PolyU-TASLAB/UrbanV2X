from pathlib import Path
import json
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores,get_typestore
ROOT=Path(__file__).resolve().parents[1]
source=Path('/media/quintinumi/data/bag/UrbanV2Xplus/2026-8-13/honda/2026-08-13-16-01-23_0.bag')
store=get_typestore(Stores.ROS1_NOETIC)
with Reader(source) as reader:
 print('Index loaded',flush=True)
 connections=[c for c in reader.connections if c.topic in ['/hikcamera/image_1/compressed','/hikcamera/image_2/compressed']]
 start=reader.start_time+38_000_000_000;done=set();out=[]
 for conn,timestamp,raw in reader.messages(connections=connections,start=start,stop=start+1_000_000_000):
  if conn.topic in done:continue
  msg=store.deserialize_ros1(raw,conn.msgtype);camera=conn.topic.split('image_')[1][0];(ROOT/f'assets/media/cam{camera}.jpg').write_bytes(msg.data.tobytes());done.add(conn.topic);out.append(dict(source=str(source),topic=conn.topic,bag_time_ns=timestamp,header=repr(msg.header),file=f'assets/media/cam{camera}.jpg'));print(conn.topic,flush=True)
  if len(done)==2:break
 (ROOT/'assets/data/camera-provenance.json').write_text(json.dumps(out,indent=2))
