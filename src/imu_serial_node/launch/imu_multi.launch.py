import os
import yaml
import serial.tools.list_ports

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


# ---------------- AUTO DETECTION FUNCTION ----------------
def detect_imu_ports():
    detected_ports = []

    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        description = port.description.lower()
        device = port.device.lower()

        # Preferred detection (USB serial chips)
        if (
            "ch340" in description or
            "cp210" in description or
            "ftdi" in description or
            "usb serial" in description
        ):
            detected_ports.append(port.device)
            continue

        # Fallback detection (Linux naming)
        if "ttyusb" in device or "ttyacm" in device:
            detected_ports.append(port.device)

    return detected_ports


# ---------------- MAIN LAUNCH FUNCTION ----------------
def generate_launch_description():

    package_share = get_package_share_directory('imu_serial_node')
    config_path = os.path.join(package_share, 'config', 'imu_params.yaml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    auto_detect = config.get("auto_detect", True)
    imu_list = config.get("imus", [])

    nodes = []
    detected_ports = []

    # -------- TRY AUTO DETECTION --------
    if auto_detect:
        detected_ports = detect_imu_ports()
        print(f"[IMU Launch] Auto-detected ports: {detected_ports}")

    # -------- IF AUTO FOUND DEVICES --------
    if auto_detect and len(detected_ports) > 0:

        print("[IMU Launch] Launching AUTO detected IMUs")

        for index, port in enumerate(detected_ports):

            node = Node(
                package='imu_serial_node',
                executable='imu_node',
                name=f'imu_node_auto_{index}',
                output='screen',
                parameters=[{
                    "port": port,
                    "baudrate": 9600,
                    "frame_id": f"imu_auto_{index}",
                    "topic_name": f"/imu_auto_{index}/data",
                    "accel_offset.x": 0.0,
                    "accel_offset.y": 0.0,
                    "accel_offset.z": 0.0,
                    "gyro_offset.x": 0.0,
                    "gyro_offset.y": 0.0,
                    "gyro_offset.z": 0.0,
                }]
            )

            nodes.append(node)

    # -------- FALLBACK TO MANUAL --------
    else:

        print("[IMU Launch] Using MANUAL configuration from YAML")

        if len(imu_list) == 0:
            print("[IMU Launch] ERROR: No manual IMUs defined in YAML!")
            return LaunchDescription([])

        for index, imu in enumerate(imu_list):

            node = Node(
                package='imu_serial_node',
                executable='imu_node',
                name=f'imu_node_manual_{index}',
                output='screen',
                parameters=[{
                    "port": imu["port"],
                    "baudrate": 9600,
                    "frame_id": imu["frame_id"],
                    "topic_name": imu["topic_name"],
                    "accel_offset.x": imu["accel_offset"]["x"],
                    "accel_offset.y": imu["accel_offset"]["y"],
                    "accel_offset.z": imu["accel_offset"]["z"],
                    "gyro_offset.x": imu["gyro_offset"]["x"],
                    "gyro_offset.y": imu["gyro_offset"]["y"],
                    "gyro_offset.z": imu["gyro_offset"]["z"],
                }]
            )

            nodes.append(node)

    return LaunchDescription(nodes)
