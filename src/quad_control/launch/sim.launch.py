from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([


        Node(
            package="quad_sim",
            executable="simulator",
            name="simulator",
            output="screen",
            parameters=[{
                "wind_amplitude": 1.0,    # амплитуда ветра 
                "wind_frequency": 0.5,    # частота ветра
            }]
        ),

        Node(
            package="quad_control",
            executable="controller",
            name="controller",
            output="screen"
        ),

        # Траектория
        Node(
            package="quad_control",
            executable="trajectory",
            name="trajectory",
            output="screen",
            parameters=[{
                # default
                "waypoints": "default",

                # задать свои точки 
                # "waypoints": "0,3,2,5,-2,4,0,6,3,3,-3,2,0,3",

                "hold_time": 5.0,         
            }]
        ),

        Node(
            package="quad_control",
            executable="rviz_scene",
            name="rviz_scene",
            output="screen"
        ),

        Node(
            package="quad_control",
            executable="metrics",
            name="metrics",
            output="screen"
        ),

        Node(
            package="quad_control",
            executable="logger",
            name="logger",
            output="screen"
        ),

        Node(
            package="quad_control",
            executable="visualizer",
            name="visualizer",
            output="screen"
        ),
    ])