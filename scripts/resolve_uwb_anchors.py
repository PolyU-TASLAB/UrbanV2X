"""Match recorded UWB ranges to supplied lamp-post coordinates without fitting positions."""
from pathlib import Path
import hashlib
import json
import numpy as np
import openpyxl
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = Path('/media/quintinumi/data/bag/UrbanV2Xplus/all_lampposts_latlon(1).xlsx')
GEOD = Geod(ellps='WGS84')


def resolve(data):
    sheet = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True).active
    candidates = []
    for row in list(sheet.values)[1:]:
        if str(row[0]).startswith('ekeo_'):
            continue
        # One source longitude contains a leading comma; the workbook stays unchanged.
        lat, lon = [float(str(value).strip().lstrip(',')) for value in row[4:6]]
        candidates.append(dict(lamppost=row[0], latitude=lat, longitude=lon))
    positions = np.array(data['positions'])[:, :2]
    first = positions[0]
    motion = np.array([GEOD.inv(first[0], first[1], p[0], p[1])[2] > 5 for p in positions])
    selected, reports = [], []
    for column, node_id in enumerate(data['ids'], 1):
        indices = [i for i, sample in enumerate(data['samples']) if motion[i] and sample[column] is not None]
        if not indices:
            continue
        observed = np.array([data['samples'][i][column] for i in indices])
        scores = []
        for candidate in candidates:
            predicted = np.array([GEOD.inv(positions[i][0], positions[i][1], candidate['longitude'], candidate['latitude'])[2] for i in indices])
            error = observed - predicted
            scores.append({**candidate, 'rmse_m': float(np.sqrt(np.mean(error ** 2))),
                           'median_absolute_error_m': float(np.median(abs(error))),
                           'p90_absolute_error_m': float(np.percentile(abs(error), 90))})
        scores.sort(key=lambda item: item['median_absolute_error_m'])
        best = scores[0]
        accepted = len(indices) >= 5 and np.ptp(observed) > 20 and best['p90_absolute_error_m'] < 3 and scores[1]['median_absolute_error_m'] - best['median_absolute_error_m'] > 10
        reports.append(dict(id=node_id, samples=len(indices), range_span_m=float(np.ptp(observed)), selected=accepted, candidates=scores))
        if accepted:
            selected.append({k: best[k] for k in ['lamppost', 'latitude', 'longitude']} | {
                'id': node_id, 'source': WORKBOOK.name, 'association': 'recorded-range consistency against tabulated positions',
                'association_inferred': True, 'height_display_only': True})
    assert any(item['id'] == 4 for item in selected)
    mapping = dict(anchors=selected, workbook=WORKBOOK.name,
                   workbook_sha256=hashlib.sha256(WORKBOOK.read_bytes()).hexdigest(),
                   comparison='WGS84 horizontal distance; moving samples over 5 m from initial GT; robust median/P90 ranking retains raw outliers; no coordinate fitting',
                   unassigned_ids=[i for i in data['ids'] if i not in [a['id'] for a in selected]], reports=reports)
    (ROOT / 'assets/data/uwb-anchor-mapping.json').write_text(json.dumps(mapping, indent=2) + '\n')
    data['mapped_nodes'] = selected
    data['mapped_node'] = next(item for item in selected if item['id'] == 4)
    return data


if __name__ == '__main__':
    path = ROOT / 'assets/data/uwb.json'
    data = resolve(json.loads(path.read_text()))
    path.write_text(json.dumps(data, separators=(',', ':')))
    timeline_path = ROOT / 'assets/data/positioning-timeline.json'
    timeline = json.loads(timeline_path.read_text())
    timeline['anchor'], timeline['anchors'] = data['mapped_node'], data['mapped_nodes']
    timeline_path.write_text(json.dumps(timeline, separators=(',', ':')))
    for anchor in data['mapped_nodes']:
        print(anchor['id'], anchor['lamppost'], anchor['latitude'], anchor['longitude'])
