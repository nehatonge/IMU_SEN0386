# IMU Serial Node (ROS 2 - Humble)

ROS 2 driver for DFRobot Serial 6-Axis Accelerometer (SEN0386).  
This node reads IMU data over UART (USB Serial), converts Roll-Pitch-Yaw to Quaternion, applies configurable calibration offsets, and publishes standard `sensor_msgs/msg/Imu` messages for visualization in RViz2.

---

## Overview

This project integrates a serial IMU sensor with ROS 2 Humble and enables:

- Real-time IMU data publishing
- Quaternion orientation output
- Angular velocity (rad/s)
- Linear acceleration (m/s²)
- YAML-based configuration
- Automatic USB detection (with manual fallback)
- Multi-IMU support
- RViz2 3D visualization

Designed for robotics learning, embedded systems, and ROS2-based development.

---

## Hardware Used

- Sensor: DFRobot Serial 6-Axis Accelerometer (SEN0386)
- Communication: UART over USB
- Baudrate: 9600

Product Wiki:  
https://wiki.dfrobot.com/Serial_6_Axis_Accelerometer_SKU_SEN0386

---

## ROS 2 Compatibility

| ROS Version | Status |
|-------------|--------|
| ROS 2 Humble | ✅ Tested |
| ROS 2 Iron | Untested |
| ROS 2 Foxy | Untested |

OS: Ubuntu 22.04

---

## Features

- Parses IMU packet format:
  - `0x55 0x51` → Acceleration
  - `0x55 0x52` → Gyroscope
  - `0x55 0x53` → Angle (Roll, Pitch, Yaw)
- Converts RPY → Quaternion
- Publishes standard ROS2 `Imu` message
- Configurable Frame ID
- Configurable topic names
- Calibration offsets via YAML
- Automatic USB port detection
- Manual serial port configuration support
- Launch-based multi-IMU support
- Compatible with RViz2 IMU display

---

## Installation

### 1️⃣ Clone Repository

```bash
cd ~
git clone https://github.com/nehatonge/IMU_SEN0386.git
cd IMU_SEN0386
```

---

### 2️⃣ Build Workspace

```bash
colcon build
```

---

### 3️⃣ Source Workspace

```bash
source install/setup.bash
```

---

## Configuration

All configuration is handled inside:

```
config/imu_params.yaml
```

Example configuration:

```yaml
auto_detect: true

imus:
  - port: "/dev/ttyUSB0"
    frame_id: "imu_front"
    topic_name: "/imu_front/data"
    accel_offset: {x: 0.01, y: -0.02, z: 0.00}
    gyro_offset: {x: 0.00, y: 0.00, z: 0.01}

  - port: "/dev/ttyUSB1"
    frame_id: "imu_rear"
    topic_name: "/imu_rear/data"
    accel_offset: {x: 0.00, y: 0.00, z: 0.00}
    gyro_offset: {x: 0.00, y: 0.00, z: 0.00}
```

### Parameter Explanation

- `auto_detect` – Enables automatic USB port detection. If detection fails, manual configuration is used.
- `port` – Serial device path (example: `/dev/ttyUSB0`)
- `frame_id` – TF frame assigned to the IMU message header
- `topic_name` – ROS2 topic where IMU data will be published
- `accel_offset` – Offset applied to linear acceleration values
- `gyro_offset` – Offset applied to angular velocity values

Offsets help correct sensor bias without modifying source code.

---

## Running the Driver

### Multi-IMU Launch

```bash
ros2 launch imu_serial_node imu_multi.launch.py
```

Each IMU defined in the YAML file runs as a separate ROS2 node.

---

## Published Topics

Each IMU publishes to its configured topic.

Example:

```
/imu_front/data
/imu_rear/data
```

Message Type:

```
sensor_msgs/msg/Imu
```

---

## Verify IMU Data

```bash
ros2 topic list
ros2 topic echo /imu_front/data
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

Set the Fixed Frame to the configured `frame_id`  
Example:

```
imu_front
```

### 3️⃣ Add IMU Display

- Click **Add**
- Select **By display type**
- Choose **Imu**
- Set Topic to:

```
/imu_front/data
```

Rotate the IMU sensor — the 3D axis should rotate accordingly.

---

## Optional: Static Transform

If required, publish a static transform:

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map imu_front
```

---

## Package Structure

```
IMU_SEN0386/
└── src/
    └── imu_serial_node/
        ├── imu_serial_node/
        │   ├── __init__.py
        │   └── imu_node.py
        │
        ├── launch/
        │   └── imu_multi.launch.py
        │
        ├── config/
        │   └── imu_params.yaml
        │
        ├── resource/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        └── README.md
```

---

## Node Details

- Node Executable: `imu_node`
- Launch File: `imu_multi.launch.py`
- Message Type: `sensor_msgs/msg/Imu`
- Baudrate: 9600
- Timer Period: 0.01s (~100 Hz)

---

## Troubleshooting

### No data in RViz

- Ensure launch file is running
- Check topic exists:
  ```bash
  ros2 topic list
  ```
- Verify Fixed Frame matches `frame_id`

### Serial Permission Error

```bash
sudo usermod -a -G dialout $USER
```

Then reboot.

### Check Serial Port

```bash
ls /dev/ttyUSB*
ls /dev/ttyACM*
```

---

## Future Improvements

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
