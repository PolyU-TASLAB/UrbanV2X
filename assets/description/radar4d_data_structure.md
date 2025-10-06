# 4D Radar Fields Specification and Usage Guide

This document describes the 4D Radar point cloud schema used in our project, the semantics and units of each field, and recommended practices for visualization and parsing in ROS1.

## Message Overview

- Topic: `/Target_Radar_1` and `/Target_Radar_1_extreme`
- Message type: `sensor_msgs/PointCloud2`
- Endianness: little-endian (ROS1 default)
- Coordinate frame: `car`
- Point layout: `point_step` and `row_step` follow standard PointCloud2 rules

## Fields Definition

Below is the `fields` array with byte offsets within each point record:

- name: x
  - offset: 0
  - datatype: 7 (FLOAT32)
  - count: 1

- name: y
  - offset: 4
  - datatype: 7 (FLOAT32)
  - count: 1

- name: z
  - offset: 8
  - datatype: 7 (FLOAT32)
  - count: 1

- name: velocity
  - offset: 16
  - datatype: 7 (FLOAT32)
  - count: 1

- name: snr
  - offset: 20
  - datatype: 7 (FLOAT32)
  - count: 1

- name: power
  - offset: 24
  - datatype: 7 (FLOAT32)
  - count: 1

- name: valid_flg
  - offset: 28
  - datatype: 4 (UINT16)
  - count: 1

- name: motion_state
  - offset: 30
  - datatype: 4 (UINT16)
  - count: 1

Note: The gap from offset 12 to 15 is reserved/padding to keep 4-byte alignment for subsequent float fields.

## Visualization Tips (RViz settings)

In the `/Target_points` display:
  - Color Transformer: Intensity
  - Channel Name: `motion_state` `power` `snr` `valid_flag` `velocity` `x` `y` `z`


## Recommended Field-to-Visualization Mappings

- Geometry: (x, y, z)
- Intensity (continuous):
  - snr (preferred) or power
  - Optional: abs(velocity) to highlight movers
- RGB (categorical):
  - motion_state mapped to color palette
- Alpha (optional):
  - Use `valid_flg` to hide invalid points (set alpha=0 for invalid)

## Parsing Examples

### C++ (ROS 1/ROS 2, sensor_msgs/PointCloud2)

```cpp
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/point_cloud2_iterator.h>

void handleCloud(const sensor_msgs::PointCloud2::ConstPtr& msg) {
  sensor_msgs::PointCloud2ConstIterator<float> it_x(*msg, "x");
  sensor_msgs::PointCloud2ConstIterator<float> it_y(*msg, "y");
  sensor_msgs::PointCloud2ConstIterator<float> it_z(*msg, "z");
  sensor_msgs::PointCloud2ConstIterator<float> it_vel(*msg, "velocity");
  sensor_msgs::PointCloud2ConstIterator<float> it_snr(*msg, "snr");
  sensor_msgs::PointCloud2ConstIterator<float> it_pow(*msg, "power");
  sensor_msgs::PointCloud2ConstIterator<uint16_t> it_valid(*msg, "valid_flg");
  sensor_msgs::PointCloud2ConstIterator<uint16_t> it_state(*msg, "motion_state");

  for (; it_x != it_x.end(); ++it_x, ++it_y, ++it_z, ++it_vel, ++it_snr, ++it_pow, ++it_valid, ++it_state) {
    const float x = *it_x;
    const float y = *it_y;
    const float z = *it_z;
    const float velocity = *it_vel;
    const float snr = *it_snr;
    const float power = *it_pow;
    const uint16_t valid = *it_valid;
    const uint16_t motion = *it_state;

    // process...
    (void)x; (void)y; (void)z; (void)velocity; (void)snr; (void)power; (void)valid; (void)motion;
  }
}