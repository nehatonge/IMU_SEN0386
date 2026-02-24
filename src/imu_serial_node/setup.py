from setuptools import setup
from glob import glob

package_name = 'imu_serial_node'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # 🔥 Install launch files
        ('share/' + package_name + '/launch', glob('launch/*.py')),

        # 🔥 Install config files
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=[
        'setuptools',
        'pyserial',
    ],
    zip_safe=True,
    maintainer='Neha Tonge',
    maintainer_email='nehatonge30@gmail.com',
    description='ROS2 driver for DFRobot Serial 6-Axis IMU (SEN0386) with auto + manual multi-IMU support.',
    license='All rights reserved',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu_node = imu_serial_node.imu_node:main',
        ],
    },
)
