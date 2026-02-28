import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/neh/IMU_SEN0386/src/imu_serial_node/install/imu_serial_node'
