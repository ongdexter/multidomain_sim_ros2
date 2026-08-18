import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def get_workspace_path():

    # This works for both installed and source workspaces
    prefix_path = os.getenv('COLCON_PREFIX_PATH', '').split(':')[0]
    if prefix_path:
        return os.path.dirname(prefix_path)  # Goes up from install/<pkg>
    return None

def generate_launch_description():
    ws_path = get_workspace_path()
    if not ws_path:
        raise RuntimeError("Could not determine workspace path!")

    sim_path = os.path.join(
        ws_path, 'src', 'multidomain_sim_ros2', 'multidomain_sim_binaries', 'multidomain_sim.x86_64'
    )
    print(f"Using simulation binary at: {sim_path}")

    # Declare config file argument
    config_arg = DeclareLaunchArgument(
        "config_file",
        default_value="unity_sim_config.yaml",
        description="Config filename (must be inside unity_interface/config)"
    )

    DeclareLaunchArgument("atsp", default_value="42")


    # Build full path: <pkg_share>/config/<config_file>
    config_path = PathJoinSubstitution([
        FindPackageShare("unity_interface"),
        LaunchConfiguration("config_file")
    ])

    return LaunchDescription([
        config_arg,
        # Node(
        #     package='ros_tcp_endpoint',
        #     executable='default_server_endpoint',
        #     name='ros_tcp_endpoint_server',
        #     output='screen',
        # ),
        ExecuteProcess(
            cmd=[sim_path, '-config', config_path],
            output='screen'
        )
    ])
