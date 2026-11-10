UrbanV2X calibration parameters

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
