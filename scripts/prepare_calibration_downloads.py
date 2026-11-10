"""Copy the supplied calibration YAMLs unchanged and build small download archives."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets/calibration'
GROUPS = ['Camera-Intrinsics', 'Extrinsics/LiDAR-Camera', 'Extrinsics/LiDAR-LiDAR',
          'Extrinsics/LiDAR-IMU', 'Extrinsics/Camera-IMU', 'Extrinsics/Camera-Camera']
README = '''UrbanV2X calibration parameters

These YAML files are copied unchanged from the supplied Camera-Intrinsics and
Extrinsics directories. Package: august_2026_reviewed_candidate.
Source status: experimental_maintenance_candidate; calibration_accepted: false.
The original status and all numerical values are preserved.

FRAMES
hdl32: Velodyne HDL-32E, /velodyne_points; onboard reference frame.
xt32: Hesai XT32, /lidar_points.
ap128p: source-file identifier for the Hesai AT128P, /lidar_points2.
imu: Xsens MTi-30, /imu/data (not the SPAN-CPT7 reference IMU).
cam0 ... cam6: /hikcamera/image_0/compressed ... /hikcamera/image_6/compressed.
Camera axes: x image-right, y image-down, z along the optical axis.
LiDAR and IMU axes follow their sensor frames in the frame diagram.
Camera positions: cam0 right-back; cam1 front-right; cam2 front-left;
cam3 left-front; cam4 right-front; cam5 left-back; cam6 rear.

SPATIAL PARAMETERS
Each transform maps source_sensor -> target_sensor, using column vectors:
  p_target = R * p_source + t
  T_target_source = [R t; 0 0 0 1]
Translations are in metres. Rotation is a flat row-major 3x3 array and
Translation is a three-element vector; matrix is a nested 4x4 array.
A_to_B.yaml maps A to B. Read source_sensor, target_sensor and maps in the file.
Camera-IMU contains imu_to_camN.yaml: IMU -> camera, despite the folder name.
camera_camera.yaml contains 21 pair transforms; cam0_from_cam1 maps cam1 -> cam0.
Reverse a transform with R_inverse = R.T, t_inverse = -R.T * t.
These onboard files do not define a global/ENU frame.

ROADSIDE PARAMETERS
rslidar_calibration contains two HKSTP and six East Kowloon LiDAR poses, with
individual YAML/JSON records and merged poses.yaml/poses.csv files.
T_Rj maps the roadside sensor frame to the declared public site ENU frame:
  p_ENU = rotation_matrix_enu_sensor * p_sensor + translation_enu_m
ENU means East, North, Up; translations are in metres. enu_anchor_lla_wgs84 is
the origin: hkstp_2a for HKSTP, ekeo_1 for East Kowloon. position_lla_wgs84 uses
degrees and WGS84 ellipsoidal height in metres. quaternion_wxyz uses [w,x,y,z].
The two sites have separate ENU origins; these are not the onboard LiDAR frame.
The supplied quality flags and usage documentation are preserved unchanged.
all_lampposts_latlon(1).xlsx contains the supplied lamp-post coordinates. These
positions are separate from the refined LiDAR sensor-origin poses above.

CAMERA INTRINSICS
Pinhole model at 2200 x 1740 pixels. cameraMatrix.data is row-major K.
distCoeffs.data contains radtan coefficients [k1, k2, p1, p2].
Camera-IMU intrinsics use [fx, fy, cx, cy] with the same distortion coefficients.

TIME PARAMETERS
Dataset-specific values are retained under time_offset_to_imu_s_by_dataset
and timeshift_cam_imu_by_dataset. Units: seconds.
Convention: t_IMU = t_sensor + offset_to_imu_s; apply each offset only once.
Use the matching aug07 or aug13 entry. These keys do not alter spatial frame direction.

SHA256SUMS lists the original file checksums. Individual files and grouped ZIPs
are available from the website Calibration page.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('/media/quintinumi/data/bag/UrbanV2Xplus'))
    args = parser.parse_args()
    paths = sorted(p for folder in ['Camera-Intrinsics', 'Extrinsics']
                   for p in (args.source / folder).rglob('*.yaml'))
    if not paths:
        raise ValueError('No calibration YAML files found')
    entries, transforms = [], []
    for path in paths:
        content = path.read_bytes()
        document = yaml.safe_load(content)
        relative = path.relative_to(args.source).as_posix()
        if relative.startswith('Camera-Intrinsics/'):
            K = np.array(document['cameraMatrix']['data']).reshape(3, 3)
            assert np.isfinite(K).all() and K[0, 0] > 0 and K[1, 1] > 0
            assert len(document['distCoeffs']['data']) == 4
        else:
            for item in document.get('transforms', {'one': document}).values():
                assert item['maps'] == f"{item['source_sensor']} -> {item['target_sensor']}"
                if 'matrix' in item:
                    T = np.array(item['matrix'], dtype=float)
                else:
                    T = np.eye(4)
                    T[:3, :3] = np.array(item['Rotation']).reshape(3, 3)
                    T[:3, 3] = item['Translation']
                assert T.shape == (4, 4) and np.isfinite(T).all()
                assert np.allclose(T[3], [0, 0, 0, 1])
                assert np.allclose(T[:3, :3].T @ T[:3, :3], np.eye(3), atol=1e-8)
                assert np.isclose(np.linalg.det(T[:3, :3]), 1, atol=1e-8)
                transforms.append((item['source_sensor'], item['target_sensor'], T))
        entries.append({'path': relative, 'bytes': len(content),
                        'sha256': hashlib.sha256(content).hexdigest(),
                        'package': document['package'], 'status': document['status'],
                        'calibration_accepted': document['calibration_accepted']})
    # Verify the supplied inverse pairs without altering or re-estimating any transform.
    by_pair = {(a, b): T for a, b, T in transforms}
    for (a, b), T in by_pair.items():
        if (b, a) in by_pair:
            assert np.allclose(T @ by_pair[(b, a)], np.eye(4), atol=1e-8)
    roadside = args.source / 'rslidar_calibration'
    roadside_count = 0
    for site in ['hkstp', 'ekeo']:
        merged = yaml.safe_load((roadside / site / 'poses.yaml').read_text())
        for record in merged['records']:
            sensor = record['sensor_id']
            y = yaml.safe_load((roadside / site / (sensor + '_lla_attitude.yaml')).read_text())
            j = json.loads((roadside / site / (sensor + '_lla_attitude.json')).read_text())
            assert record == y == j
            assert record['enu_anchor_lla_wgs84'] == merged['enu_anchor_lla_wgs84']
            pose = record['T_Rj']
            R = np.array(pose['rotation_matrix_enu_sensor'])
            q = np.array(pose['quaternion_wxyz'])
            assert np.allclose(R.T @ R, np.eye(3), atol=1e-8)
            assert np.isclose(np.linalg.det(R), 1, atol=1e-8)
            assert np.isclose(np.linalg.norm(q), 1, atol=1e-8)
            assert np.allclose(pose['translation_enu_m'], record['position_enu_m'])
            roadside_count += 1
    for path in sorted(p for p in roadside.rglob('*') if p.is_file()) + [args.source / 'all_lampposts_latlon(1).xlsx']:
        content = path.read_bytes()
        entries.append({'path': path.relative_to(args.source).as_posix(), 'bytes': len(content),
                        'sha256': hashlib.sha256(content).hexdigest(), 'kind': 'roadside'})
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        target = OUTPUT / entry['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.source / entry['path'], target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == entry['sha256']
    (OUTPUT / 'README.txt').write_text(README)
    (OUTPUT / 'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['path']}\n" for e in entries))
    archive_sets = {'UrbanV2X-calibration.zip': entries,
                    'Camera-Intrinsics.zip': [e for e in entries if e['path'].startswith('Camera-Intrinsics/')],
                    'Extrinsics.zip': [e for e in entries if not e['path'].startswith('Camera-Intrinsics/')]}
    archive_sets['Roadside.zip'] = [e for e in entries if e.get('kind') == 'roadside']
    for site in ['hkstp', 'ekeo']:
        archive_sets[f'Roadside-{site}.zip'] = [e for e in entries if e['path'].startswith(f'rslidar_calibration/{site}/')]
    for group in GROUPS[1:]:
        archive_sets[group.split('/')[-1] + '.zip'] = [e for e in entries if e['path'].startswith(group + '/')]
    archives = []
    for name, subset in archive_sets.items():
        with zipfile.ZipFile(OUTPUT / name, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            files = {e['path']: (OUTPUT / e['path']).read_bytes() for e in subset}
            files['README.txt'] = README.encode()
            files['SHA256SUMS'] = ''.join(f"{e['sha256']}  {e['path']}\n" for e in subset).encode()
            for relative, content in sorted(files.items()):
                info = zipfile.ZipInfo('UrbanV2X-calibration/' + relative, date_time=(2026, 11, 10, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, content)
        archives.append({'name': name, 'files': len(subset), 'bytes': (OUTPUT / name).stat().st_size})
    manifest = {'files': entries, 'archives': archives, 'transform_count': len(transforms), 'roadside_poses': roadside_count,
                'raw_bytes': sum(e['bytes'] for e in entries), 'source_values_unchanged': True}
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'files': len(entries), 'transforms': len(transforms), 'raw_bytes': manifest['raw_bytes'], 'archives': archives}, indent=2))


if __name__ == '__main__':
    main()
