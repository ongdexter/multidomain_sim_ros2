#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import math

class QuadrotorController(Node):
    def __init__(self):
        super().__init__('quadrotor_control')
        # Topic prefix follows the robot 'name' in the sim config (e.g. /uav1/pose_cmd)
        self.declare_parameter('pose_cmd_topic', '/uav/pose_cmd')
        self.declare_parameter('center', [5.0, -5.0, 30.0])
        self.declare_parameter('radius', 10.0)
        self.declare_parameter('angular_speed', 0.2)  # radians per second

        topic = self.get_parameter('pose_cmd_topic').value
        self.center = self.get_parameter('center').value
        self.radius = self.get_parameter('radius').value
        self.angular_speed = self.get_parameter('angular_speed').value

        self.pub = self.create_publisher(Pose, topic, 10)
        self.timer_period = 0.1  # seconds (10 Hz)
        self.create_timer(self.timer_period, self.publish_pose)
        self.angle = 0.0
        self.pose = Pose()
        self.pose.orientation.w = 1.0
        self.get_logger().info(f'Publishing pose commands on {topic}')

    def publish_pose(self):
        # Circle around 'center' at 'radius', advancing at 'angular_speed'
        self.pose.position.x = self.center[0] + self.radius * math.cos(self.angle)
        self.pose.position.y = self.center[1] + self.radius * math.sin(self.angle)
        self.pose.position.z = self.center[2]

        self.angle += self.angular_speed * self.timer_period
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi

        self.pub.publish(self.pose)
        self.get_logger().info(f'Published quadrotor pose: {self.pose.position.x:.2f}, {self.pose.position.y:.2f}, {self.pose.position.z:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = QuadrotorController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()
