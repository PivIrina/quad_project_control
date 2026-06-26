from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'quad_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', 'quad_control', 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "controller=quad_control.controller_node:main",
            "trajectory=quad_control.trajectory_node:main",
            "logger=quad_control.logger_node:main",
            "visualizer=quad_control.visualizer_node:main",
            "metrics=quad_control.metrics_node:main",
            "rviz_scene=quad_control.rviz_scene_node:main",
        ],
    },
)
