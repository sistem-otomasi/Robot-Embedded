"""Video Publisher Package"""
from setuptools import setup

package_name = 'video_publisher'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robot Team',
    maintainer_email='robot@example.com',
    description='Video file publisher for ROS2 Humble',
    license='MIT',
)
