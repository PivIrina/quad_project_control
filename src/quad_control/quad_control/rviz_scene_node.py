import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
from math import sin, cos


class RvizScene(Node):

    def __init__(self):
        super().__init__("rviz_scene")

        self.x = 0.0
        self.z = 0.0
        self.theta = 0.0
        self.xr = 0.0
        self.zr = 0.0
        self.traj_points = []

        self.create_subscription(Float32MultiArray, "/quad/state", self.state_cb, 10)
        self.create_subscription(Float32MultiArray, "/quad/reference", self.ref_cb, 10)

        self.drone_pub = self.create_publisher(Marker, "/rviz/drone", 10)
        self.traj_pub = self.create_publisher(Marker, "/rviz/traj", 10)
        self.corridor_pub = self.create_publisher(MarkerArray, "/rviz/corridor", 10)
        self.ref_pub = self.create_publisher(Marker, "/rviz/ref", 10)

        self.timer = self.create_timer(0.05, self.update)

    def state_cb(self, msg):
        self.x = msg.data[0]
        self.z = msg.data[1]
        self.theta = msg.data[2]
        self.traj_points.append((self.x, self.z))

    def ref_cb(self, msg):
        self.xr = msg.data[0]
        self.zr = msg.data[1]

    def publish_corridor(self):
        walls = MarkerArray()
        for i, x in enumerate([-5.0, 5.0]):
            m = Marker()
            m.header.frame_id = "world"
            m.header.stamp = self.get_clock().now().to_msg()
            m.id = i
            m.type = Marker.CUBE
            m.action = Marker.ADD
            m.scale.x = 0.05
            m.scale.y = 10.0
            m.scale.z = 0.05
            m.color.a = 1.0
            m.color.g = 0.8
            m.pose.position.x = float(x)
            m.pose.position.y = 5.0
            m.pose.position.z = 0.0
            walls.markers.append(m)
        self.corridor_pub.publish(walls)

    def publish_drone(self):
        m = Marker()
        m.header.frame_id = "world"
        m.header.stamp = self.get_clock().now().to_msg()
        m.type = Marker.CUBE
        m.action = Marker.ADD
        m.scale.x = 0.25
        m.scale.y = 0.1
        m.scale.z = 0.05
        m.color.a = 1.0
        m.color.r = 1.0
        m.pose.position.x = self.x
        m.pose.position.y = self.z
        m.pose.position.z = 0.0
        m.pose.orientation.z = sin(self.theta / 2.0)
        m.pose.orientation.w = cos(self.theta / 2.0)
        self.drone_pub.publish(m)

    def publish_traj(self):
        m = Marker()
        m.header.frame_id = "world"
        m.header.stamp = self.get_clock().now().to_msg()
        m.type = Marker.LINE_STRIP
        m.action = Marker.ADD
        m.scale.x = 0.02
        m.color.a = 1.0
        m.color.b = 1.0
        for p in self.traj_points[-500:]:
            pt = Point()
            pt.x = float(p[0])
            pt.y = float(p[1])
            pt.z = 0.0
            m.points.append(pt)
        self.traj_pub.publish(m)

    def publish_ref(self):
        m = Marker()
        m.header.frame_id = "world"
        m.header.stamp = self.get_clock().now().to_msg()
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.scale.x = 0.15
        m.scale.y = 0.15
        m.scale.z = 0.15
        m.color.a = 1.0
        m.color.g = 1.0
        m.color.b = 1.0
        m.pose.position.x = self.xr
        m.pose.position.y = self.zr
        m.pose.position.z = 0.0
        self.ref_pub.publish(m)

    def update(self):
        self.publish_corridor()
        self.publish_drone()
        self.publish_traj()
        self.publish_ref()


def main():
    rclpy.init()
    rclpy.spin(RvizScene())
    rclpy.shutdown()