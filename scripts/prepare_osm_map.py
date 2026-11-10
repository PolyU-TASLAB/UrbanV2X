"""Fetch OSM geometry for the HKSTP scene; annotations belong to the webpage."""
from pathlib import Path
import json,urllib.request,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.openstreetmap.org/api/0.6/map?bbox=114.211,22.422,114.217,22.427'
request=urllib.request.Request(URL,headers={'User-Agent':'UrbanV2X-research-site/1.0'})
with urllib.request.urlopen(request,timeout=40) as response: root=ET.fromstring(response.read())
nodes={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in root.findall('node')};features=[]
for way in root.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')};kind='building' if 'building' in tags else 'road' if 'highway' in tags else None
 if not kind:continue
 points=[nodes[n.attrib['ref']] for n in way.findall('nd') if n.attrib['ref'] in nodes]
 try:height=float(tags.get('height',str(float(tags.get('building:levels','4'))*3.3)).replace('m','').strip())
 except ValueError:height=13.2
 features.append(dict(kind=kind,points=points,height=height,estimated_height='height' not in tags and 'building:levels' not in tags))
(ROOT/'assets/data/hkstp-map.json').write_text(json.dumps(dict(source='OpenStreetMap contributors',url=URL,bbox=[114.211,22.422,114.217,22.427],features=features),separators=(',',':')))
