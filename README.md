# Multidomain Sim ROS 2

A ROS 2 interface to a Unity-based multi-domain simulator. The simulator ships as a
prebuilt Linux binary and talks to ROS 2 through the
[Unity ROS-TCP-Endpoint](https://github.com/Unity-Technologies/ROS-TCP-Endpoint).
It can spawn multiple robots (aerial and ground) in the same scene, each with its own
sensor suite and its own topic namespace.

## Contents

| Path | What it is |
| --- | --- |
| [unity_interface/](unity_interface/) | ROS 2 (`ament_cmake`) package: launch files, sim configs, example control node |
| [multidomain_sim_binaries/](multidomain_sim_binaries/) | Prebuilt Unity player (`multidomain_sim.x86_64`) and its data, as a Git LFS submodule |
| [ROS-TCP-Endpoint/](ROS-TCP-Endpoint/) | Unity's ROS 2 TCP endpoint, vendored as a submodule |

## Requirements

- ROS 2 (tested on Humble)
- A Linux machine with a GPU — the simulator renders camera and depth sensors
- `colcon`, plus the usual `rclpy` / `rclcpp` / `geometry_msgs` / `sensor_msgs` / `nav_msgs` packages

## Setup

The simulator binaries are large and tracked with Git LFS, so install LFS support before
cloning:

```bash
git lfs install
cd ~/ros2_sim_ws/src
git clone --recursive https://github.com/ongdexter/multidomain_sim_ros2.git multidomain_sim_ros2
cd multidomain_sim_ros2
```

`--recursive` pulls both submodules: `ROS-TCP-Endpoint` from GitHub, and
`multidomain_sim_binaries` from the lab GitLab at `158.130.118.32:8929`. Expect roughly 11 GB.

Then build and source the workspace:

```bash
cd ~/ros2_sim_ws
colcon build --symlink-install
source install/setup.bash
```

> The launch files locate the simulator through `COLCON_PREFIX_PATH`, so the workspace
> **must** be sourced, and the repo must sit at `<workspace>/src/multidomain_sim_ros2`.

## Running

Start everything (TCP endpoint + simulator) with one command:

```bash
ros2 launch unity_interface sim_with_endpoint.launch.py
```

Other launch files:

| Launch file | What it does |
| --- | --- |
| `sim_with_endpoint.launch.py` | ROS-TCP-Endpoint **and** the simulator, using `unity_interface/config/unity_sim_config.yaml` |
| `sim.launch.py` | Simulator only (assumes an endpoint is already running) |
| `sim_with_config_arg.launch.py` | Simulator only, with a selectable config: `config_file:=<name>.yaml` |
| `endpoint.launch.py` | ROS-TCP-Endpoint only |
| `quadrotor_control.launch.py` | Example node that flies a circular trajectory |

Pick a different config (the file must be installed into the package share directory,
i.e. live in `unity_interface/config/`):

```bash
ros2 launch unity_interface sim_with_config_arg.launch.py config_file:=unity_sim_forest_pos1_config.yaml
```

The endpoint listens on `0.0.0.0:10000` by default; override with

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0 -p ROS_TCP_PORT:=10000
```

## ROS interface

Every robot listed in the config gets its own namespace, taken from its `name` field.
With the default config (`uav`, `ugv`) the topics are:

### UAV

| Topic | Type | Notes |
| --- | --- | --- |
| `/uav/pose_cmd` | `geometry_msgs/Pose` | **Input.** Commanded pose (position + orientation) |
| `/uav/pose` | `geometry_msgs/PoseStamped` | Current pose |
| `/uav/odom` | `nav_msgs/Odometry` | Current odometry |
| `/uav/color/image` | `sensor_msgs/Image` | RGB, `rgb8` |
| `/uav/color/info` | `sensor_msgs/CameraInfo` | RGB camera intrinsics |
| `/uav/depth/image` | `sensor_msgs/Image` | `16UC1`, millimeters |
| `/uav/depth/info` | `sensor_msgs/CameraInfo` | Depth camera intrinsics |
| `/uav/depth/points` | `sensor_msgs/PointCloud2` | Point cloud from the depth camera |

### UGV

| Topic | Type | Notes |
| --- | --- | --- |
| `/ugv/pose_cmd` | `geometry_msgs/Pose` | **Input.** Commanded pose |
| `/ugv/pose` | `geometry_msgs/PoseStamped` | Current pose |
| `/ugv/odom` | `nav_msgs/Odometry` | Current odometry |
| `/ugv/color_front/image`, `/ugv/color_back/image`, `/ugv/color_left/image`, `/ugv/color_right/image` | `sensor_msgs/Image` | Four-camera ring, `rgb8` |
| `/ugv/color_front/info`, `/ugv/color_back/info`, `/ugv/color_left/info`, `/ugv/color_right/info` | `sensor_msgs/CameraInfo` | Per-camera intrinsics |
| `/ugv/depth/image` | `sensor_msgs/Image` | `16UC1`, millimeters |
| `/ugv/depth/info` | `sensor_msgs/CameraInfo` | Depth camera intrinsics |
| `/ugv/depth/points` | `sensor_msgs/PointCloud2` | Point cloud from the depth camera |
| `/ugv/velodyne_points` | `sensor_msgs/PointCloud2` | 3D LiDAR |

If you rename a robot to `uav1`, its topics become `/uav1/pose_cmd`, `/uav1/pose`, and so on.

Minimal example — command the UAV to a pose:

```bash
ros2 topic pub /uav/pose_cmd geometry_msgs/msg/Pose \
  "{position: {x: 10.0, y: 0.0, z: 30.0}, orientation: {w: 1.0}}"
```

## Configuration

The simulator is driven by a YAML file passed with `-config <path>`; the launch files
pass `unity_interface/config/unity_sim_config.yaml`. If no config is given, the player
falls back to the copy baked into
`multidomain_sim_binaries/multidomain_sim_Data/StreamingAssets/unity_sim_config.yaml`.

All robot poses are in **ROS coordinates (ENU, Z-up)**. Mesh transforms in
`customEnvironments` are in **Unity world space** (Y-up).

```yaml
environment: PolyCityScene        # scene to load on startup

# Robots to spawn. Each is cloned from the scene template.
# 'name' sets both the GameObject name and the ROS topic prefix.
# 'type' is 'uav' or 'ugv'.
robots:
  - name: uav
    type: uav
    startPosition: {x: 0.0, y: 0.0, z: 30.0}
    startOrientation: {roll: 0.0, pitch: 0.0, yaw: 0.0}
  - name: ugv
    type: ugv
    startPosition: {x: 0.0, y: 0.0, z: 1.0}
    startOrientation: {roll: 0.0, pitch: 0.0, yaw: 0.0}

# Per-scene overrides, applied when that scene is loaded.
# The keys under 'robots' must match the names used above.
sceneStartPoses:
  - scene: ForestScene
    robots:
      uav:
        startPosition: {x: -15.0, y: -50.0, z: 120.0}
        startOrientation: {roll: 0.0, pitch: 0.0, yaw: 0.0}

# Environments built from your own GLB meshes.
# GLB paths are relative to the player's Assets/ folder, or absolute.
# colliderMesh is optional — renderMesh is used for collision if it is omitted.
customEnvironments:
  - scene: PennovationScene
    renderMesh:
      glb: sfm_meshes/pennovation_sfm_mesh_20m.glb
      position: {x: 0.0, y: 26.6, z: 0.0}
      rotation: {x: 0.0, y: 180.0, z: 0.0}
    colliderMesh:
      glb: sfm_meshes/pennovation_sfm_mesh_500k.glb
      position: {x: 0.0, y: 26.6, z: 0.0}
      rotation: {x: 0.0, y: 180.0, z: 0.0}
    robots:
      uav:
        startPosition: {x: -30.0, y: -35.0, z: 40.0}
        startOrientation: {roll: 0.0, pitch: 0.0, yaw: 0.0}
```

### Environments

Built into the player:

- `PolyCityScene` — urban environment
- `ForestScene` — forest / off-road
- `FloodedGroundsScene` — flooded terrain

Loaded at runtime from GLB meshes via `customEnvironments` (see the shipped config):

- `PennovationScene`, `DiningHallScene`, `Range15Scene`

To add your own, append an entry to `customEnvironments` with a scene name, the GLB
paths, the mesh transform, and the robot start poses. No rebuild of the player is needed.


## Example control node

[unity_interface/scripts/quadrotor_control.py](unity_interface/scripts/quadrotor_control.py)
publishes a circular pose trajectory at 10 Hz — a small template for writing your own
controller:

```bash
ros2 launch unity_interface quadrotor_control.launch.py
ros2 launch unity_interface quadrotor_control.launch.py pose_cmd_topic:=/uav1/pose_cmd
```

Its `center`, `radius`, and `angular_speed` parameters control the trajectory.

## Troubleshooting

- **"Could not determine workspace path!"** — the workspace was not sourced. Run
  `source install/setup.bash` before launching.
- **Simulator starts but no topics appear** — the endpoint is not running or is on a
  different port. Start it with `endpoint.launch.py` and check that the sim connects to
  port `10000`.
- **Simulator fails to start** — you may need to run `chmod +x multidomain_sim_binaries/multidomain_sim.x86_64`.
- **Custom environment loads empty** — the `glb` path is resolved relative to the
  player's `Assets/` folder; use an absolute path if the mesh lives elsewhere.
