import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import serial
import struct
import math


class IMUSerialNode(Node):

    def __init__(self):
        super().__init__('imu_serial_node')

        self.publisher_ = self.create_publisher(Imu, 'imu/data', 10)

        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        self.acc = [0.0, 0.0, 0.0]
        self.gyro = [0.0, 0.0, 0.0]
        self.q = [0.0, 0.0, 0.0, 1.0]  # Default valid quaternion

        self.timer = self.create_timer(0.01, self.read_imu)

    def read_imu(self):

        while self.ser.in_waiting > 0:

            byte = self.ser.read(1)

            if byte == b'\x55':

                packet = self.ser.read(10)

                if len(packet) < 10:
                    return

                data = b'\x55' + packet

                # Acceleration packet (0x51)
                if data[1] == 0x51:
                    self.acc[0] = struct.unpack('<h', data[2:4])[0] / 32768.0 * 16 * 9.81
                    self.acc[1] = struct.unpack('<h', data[4:6])[0] / 32768.0 * 16 * 9.81
                    self.acc[2] = struct.unpack('<h', data[6:8])[0] / 32768.0 * 16 * 9.81

                # Gyroscope packet (0x52)
                elif data[1] == 0x52:
                    self.gyro[0] = struct.unpack('<h', data[2:4])[0] / 32768.0 * 2000 * math.pi / 180
                    self.gyro[1] = struct.unpack('<h', data[4:6])[0] / 32768.0 * 2000 * math.pi / 180
                    self.gyro[2] = struct.unpack('<h', data[6:8])[0] / 32768.0 * 2000 * math.pi / 180

                # Angle packet (0x53)
                elif data[1] == 0x53:

                    roll = struct.unpack('<h', data[2:4])[0] / 32768.0 * 180
                    pitch = struct.unpack('<h', data[4:6])[0] / 32768.0 * 180
                    yaw = struct.unpack('<h', data[6:8])[0] / 32768.0 * 180

                    roll = math.radians(roll)
                    pitch = math.radians(pitch)
                    yaw = math.radians(yaw)

                    cy = math.cos(yaw * 0.5)
                    sy = math.sin(yaw * 0.5)
                    cp = math.cos(pitch * 0.5)
                    sp = math.sin(pitch * 0.5)
                    cr = math.cos(roll * 0.5)
                    sr = math.sin(roll * 0.5)

                    self.q[0] = sr * cp * cy - cr * sp * sy
                    self.q[1] = cr * sp * cy + sr * cp * sy
                    self.q[2] = cr * cp * sy - sr * sp * cy
                    self.q[3] = cr * cp * cy + sr * sp * sy

        # Publish IMU message
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

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


if __name__ == '__main__':
    main()
