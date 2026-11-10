"""Read sampled UWB messages and the matching reference positions; no raw writes."""
from pathlib import Path
import json, numpy as np
ROOT=Path(__file__).resolve().parents[1];SOURCE=Path('/media/quintinumi/data/bag/UrbanV2Xplus/2026-8-13/honda/2026-08-13-16-01-23_0.bag')
def export(records):
 track=np.load(ROOT.parent/'ws_urbanv2x_ijrr/metadata/trajectory_maps/honda_2.npz');ts=track['time_ns']/1e9;t0=records[0]['utc'];rows=[];positions=[]
 for record in records:
  readings={}
  for node in record['nodes']:
   if node['distance_m']>0: readings.setdefault(node['id'],round(node['distance_m'],3))
  rows.append([round(record['utc']-t0,3)]+[readings.get(i) for i in [1,3,4,18]])
  k=int(np.argmin(abs(ts-record['utc'])));positions.append([float(track['longitude'][k]),float(track['latitude'][k]),float(ts[k]-record['utc'])])
 data=dict(source=str(SOURCE),topic='/nlink_linktrack_nodeframe3',start_unix_s=t0,ids=[1,3,4,18],samples=rows,positions=positions,duration_s=rows[-1][0],sampling='First message at least 0.5 s after the previous selected message; first valid entry per node ID; no interpolation or gap filling.')
 from resolve_uwb_anchors import resolve
 data=resolve(data)
 (ROOT/'assets/data/uwb.json').write_text(json.dumps(data,separators=(',',':')))
if __name__=='__main__':
 from rosbags.rosbag1 import Reader
 from rosbags.typesys import Stores,get_typestore,get_types_from_msg
 store=get_typestore(Stores.ROS1_NOETIC);records=[];next_time=0
 with Reader(SOURCE) as reader:
  connection=next(c for c in reader.connections if c.topic=='/nlink_linktrack_nodeframe3');store.register(get_types_from_msg(connection.msgdef.data,connection.msgtype))
  for conn,t,raw in reader.messages(connections=[connection]):
   if t<next_time:continue
   msg=store.deserialize_ros1(raw,conn.msgtype);next_time=t+500000000
   records.append(dict(utc=t/1e9,nodes=[dict(id=n.id,distance_m=float(n.dis)) for n in msg.nodes]))
 export(records)
