from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'pose_cmd_topic',
            default_value='/uav/pose_cmd',
            description="Pose command topic; matches the robot 'name' in the sim config"
        ),
        Node(
            package='unity_interface',
            executable='quadrotor_control.py',
            name='quadrotor_control',
            output='screen',
            parameters=[{'pose_cmd_topic': LaunchConfiguration('pose_cmd_topic')}],
        ),
    ])
