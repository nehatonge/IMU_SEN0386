import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from rcl_interfaces.msg import SetParametersResult
from std_srvs.srv import Trigger
import serial
import struct
import math
import sqlite3
import os


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

        # -------- DATABASE INIT --------
        self.init_database()
        self.load_latest_calibration()

        # Save calibration service
        self.save_service = self.create_service(
            Trigger,
            'save_calibration',
            self.save_calibration_callback
        )

        self.publisher_ = self.create_publisher(Imu, topic_name, 10)

        self.get_logger().info(f"Using IMU port: {port}")
        self.ser = serial.Serial(port, baudrate, timeout=1)

        self.acc = [0.0, 0.0, 0.0]
        self.gyro = [0.0, 0.0, 0.0]
        self.q = [0.0, 0.0, 0.0, 1.0]

        self.timer = self.create_timer(0.01, self.read_imu)
        self.logTimer = self.create_timer(1, self.log_data)

        # Enable dynamic parameter updates
        self.add_on_set_parameters_callback(self.parameter_callback)

    def log_data(self):
        self.get_logger().warn(f"Gyro X offset: {self.gyro_offset[0]}")

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

    #  Dynamic Parameter Callback
    def parameter_callback(self, params):

        for param in params:

            if param.name == 'accel_offset.x':
                if self.accel_offset[0] != param.value:
                    self.accel_offset[0] = param.value
                    self.save_single_param(param.name, param.value)

            elif param.name == 'accel_offset.y':
                if self.accel_offset[1] != param.value:
                    self.accel_offset[1] = param.value
                    self.save_single_param(param.name, param.value)

            elif param.name == 'accel_offset.z':
                if self.accel_offset[2] != param.value:
                    self.accel_offset[2] = param.value
                    self.save_single_param(param.name, param.value)

            elif param.name == 'gyro_offset.x':
                if self.gyro_offset[0] != param.value:
                    self.gyro_offset[0] = param.value
                    self.save_single_param(param.name, param.value)

            elif param.name == 'gyro_offset.y':
                if self.gyro_offset[1] != param.value:
                    self.gyro_offset[1] = param.value
                    self.save_single_param(param.name, param.value)

            elif param.name == 'gyro_offset.z':
                if self.gyro_offset[2] != param.value:
                    self.gyro_offset[2] = param.value
                    self.save_single_param(param.name, param.value)

        return SetParametersResult(successful=True)
   
    # -------- DATABASE FUNCTIONS --------

    def init_database(self):
        db_path = os.path.join(os.getcwd(), "imu_calibration.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS imu_calibration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                frame_id TEXT,
                param_name TEXT,
                value REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
            

    def load_latest_calibration(self):

        try:
            self.cursor.execute("""
                SELECT param_name, value
                FROM imu_calibration_history
                WHERE frame_id = ?
                ORDER BY id ASC
            """, (self.frame_id,))

            rows = self.cursor.fetchall()

            if not rows:
                self.get_logger().info("No calibration history found.")
                return

            for param_name, value in rows:

                if param_name == 'accel_offset.x':
                    self.accel_offset[0] = value

                elif param_name == 'accel_offset.y':
                    self.accel_offset[1] = value

                elif param_name == 'accel_offset.z':
                    self.accel_offset[2] = value

                elif param_name == 'gyro_offset.x':
                    self.gyro_offset[0] = value

                elif param_name == 'gyro_offset.y':
                    self.gyro_offset[1] = value

                elif param_name == 'gyro_offset.z':
                    self.gyro_offset[2] = value

            self.get_logger().info("Loaded calibration from delta history.")

        except Exception as e:
            self.get_logger().error(f"Database load failed: {e}")
    def save_single_param(self, param_name, value):

        self.cursor.execute("""
            INSERT INTO imu_calibration_history
            (frame_id, param_name, value)
            VALUES (?, ?, ?)
        """, (
            self.frame_id,
            param_name,
            value
        ))

        self.conn.commit()
        self.get_logger().info(f"Saved {param_name} to database.")
    def save_calibration_callback(self, request, response):
        response.success = True
        response.message = "Delta model auto-saves parameters."
        return response


def main(args=None):
    rclpy.init(args=args)
    node = IMUSerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()