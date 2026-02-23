# IMU Serial Node (ROS 2 - Humble)

ROS 2 driver for DFRobot Serial 6-Axis Accelerometer (SEN0386).  
This node reads IMU data over UART (USB Serial), converts Roll-Pitch-Yaw to Quaternion, and publishes standard `sensor_msgs/msg/Imu` messages for visualization in RViz2.

---

## Overview

This project integrates a serial IMU sensor with ROS 2 Humble and enables:

- Real-time IMU data publishing
- Quaternion orientation output
- Angular velocity (rad/s)
- Linear acceleration (m/s²)
- RViz2 3D visualization

Designed for robotics learning, embedded systems, and ROS2-based development.

---

## Hardware Used

- Sensor: DFRobot Serial 6-Axis Accelerometer (SEN0386)
- Communication: UART over USB
- Default Port: `/dev/ttyUSB0`
- Baudrate: 9600

Product Wiki:  
https://wiki.dfrobot.com/Serial_6_Axis_Accelerometer_SKU_SEN0386

---

## ROS 2 Compatibility

| ROS Version | Status |
|-------------|--------|
| ROS 2 Humble | ✅ Tested |

 OS: Ubuntu 22.04

---

## Features

- Parses IMU packet format:
  - `0x55 0x51` → Acceleration
  - `0x55 0x52` → Gyroscope
  - `0x55 0x53` → Angle (Roll, Pitch, Yaw)
- Converts RPY → Quaternion
- Publishes standard ROS2 `Imu` message
- Frame ID: `base_link`
- Approx. 100 Hz publishing rate
- Compatible with RViz2 IMU display

---

## Installation

### 1️⃣ Place package in workspace

```bash
cd ~/ros2_ws/src
```

Add the `imu_serial_node` package inside `src`.

---

### 2️⃣ Build Workspace

```bash
cd ~/ros2_ws
colcon build
```

---

### 3️⃣ Source ROS 2 and Workspace

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

---

## Running the Node

```bash
ros2 run imu_serial_node imu_node
```

The node publishes:

```
/imu/data  →  sensor_msgs/msg/Imu
```

---

## Verify IMU Data

```bash
ros2 topic echo /imu/data
```

You should see:

- Header
- Orientation (x, y, z, w)
- Angular velocity
- Linear acceleration

---

## RViz2 Visualization

### 1️⃣ Launch RViz2

```bash
rviz2
```

### 2️⃣ Set Fixed Frame

```
base_link
```

### 3️⃣ Add IMU Display

- Click **Add**
- Select **By display type**
- Choose **Imu**
- Set Topic to:

```
/imu/data
```

Rotate the IMU sensor — the 3D axis should rotate accordingly.

---

## Optional: Static Transform

If required, publish a static transform:

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map base_link
```

---

## Package Structure

```
imu_serial_node/
│
├── imu_node.py
├── package.xml
├── setup.py
├── setup.cfg
└── README.md
```

---

## Node Details

- Node Name: `imu_serial_node`
- Topic: `/imu/data`
- Message Type: `sensor_msgs/msg/Imu`
- Frame ID: `base_link`
- Timer Period: 0.01s (~100 Hz)

---

## Troubleshooting

### No data in RViz

- Ensure node is running
- Check topic exists:
  ```bash
  ros2 topic list
  ```
- Set Fixed Frame = `base_link`

### Serial Permission Error

```bash
sudo usermod -a -G dialout $USER
```

Then reboot.

### Check Serial Port

```bash
ls /dev/ttyUSB*
```

---

## Future Improvements

- Launch file integration
- Dynamic TF broadcasting
- Covariance matrix estimation
- Sensor calibration routine
- URDF + RobotModel visualization
- ROS2 bag recording support

---

## Author

Neha Tonge  
Electronics Engineering (VLSI Major, Robotics Minor)  
ROS 2 & Embedded Systems Developer  

---

## License

© 2026 Neha Tonge.  
All rights reserved.
