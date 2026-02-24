import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import serial
import struct
import math


class IMUSerialNode(Node):

    def __init__(self):
        super().__init__('imu_serial_node')

        # Declare parameters
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('frame_id', 'base_link')
        self.declare_parameter('topic_name', '/imu/data')

        self.declare_parameter('accel_offset.x', 0.0)
        self.declare_parameter('accel_offset.y', 0.0)
        self.declare_parameter('accel_offset.z', 0.0)

        self.declare_parameter('gyro_offset.x', 0.0)
        self.declare_parameter('gyro_offset.y', 0.0)
        self.declare_parameter('gyro_offset.z', 0.0)

        # Get parameters
        port = self.get_parameter('port').get_parameter_value().string_value
        baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        topic_name = self.get_parameter('topic_name').get_parameter_value().string_value

        self.accel_offset = [
            self.get_parameter('accel_offset.x').value,
            self.get_parameter('accel_offset.y').value,
            self.get_parameter('accel_offset.z').value,
        ]

        self.gyro_offset = [
            self.get_parameter('gyro_offset.x').value,
            self.get_parameter('gyro_offset.y').value,
            self.get_parameter('gyro_offset.z').value,
        ]

        self.publisher_ = self.create_publisher(Imu, topic_name, 10)

        self.get_logger().info(f"Using IMU port: {port}")
        self.ser = serial.Serial(port, baudrate, timeout=1)

        self.acc = [0.0, 0.0, 0.0]
        self.gyro = [0.0, 0.0, 0.0]
        self.q = [0.0, 0.0, 0.0, 1.0]

        self.timer = self.create_timer(0.01, self.read_imu)

    def read_imu(self):

        while self.ser.in_waiting > 0:
            byte = self.ser.read(1)

            if byte == b'\x55':
                packet = self.ser.read(10)
                if len(packet) < 10:
                    return

                data = b'\x55' + packet

                if data[1] == 0x51:
                    for i in range(3):
                        raw = struct.unpack('<h', data[2+i*2:4+i*2])[0]
                        self.acc[i] = raw / 32768.0 * 16 * 9.81 - self.accel_offset[i]

                elif data[1] == 0x52:
                    for i in range(3):
                        raw = struct.unpack('<h', data[2+i*2:4+i*2])[0]
                        self.gyro[i] = raw / 32768.0 * 2000 * math.pi / 180 - self.gyro_offset[i]

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        msg.orientation.x = self.q[0]
        msg.orientation.y = self.q[1]
        msg.orientation.z = self.q[2]
        msg.orientation.w = self.q[3]

        msg.linear_acceleration.x = self.acc[0]
        msg.linear_acceleration.y = self.acc[1]
        msg.linear_acceleration.z = self.acc[2]

        msg.angular_velocity.x = self.gyro[0]
        msg.angular_velocity.y = self.gyro[1]
        msg.angular_velocity.z = self.gyro[2]

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = IMUSerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
