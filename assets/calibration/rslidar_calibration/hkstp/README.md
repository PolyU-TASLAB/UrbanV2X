# Public HKSTP roadside LiDAR poses

每条记录提供 WGS84 LLA，以及从雷达坐标系到 `poses.yaml` 中所列站点 ENU 原点的 `T_Rj`。
完整坐标定义、矩阵方向、角度和四元数约定、ROS TF 用法见 [外参使用说明](../外参使用说明.md)。
这些文件不包含 `T_map_sensor`、私有地图原点、地图路径或点云路径。
