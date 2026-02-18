"""LaneNet Detector Package"""
from setuptools import setup

package_name = 'lanenet_detector'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robot Team',
    maintainer_email='robot@example.com',
    description='LaneNet lane detection package for ROS2 Humble',
    license='MIT',
)
