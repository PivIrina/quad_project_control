import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class TrajectoryNode(Node):

    def __init__(self):
        super().__init__("trajectory")

        self.declare_parameter("waypoints", "default")
        self.declare_parameter("hold_time", 5.0)

        wp_raw = self.get_parameter("waypoints").value
        self.hold_time = self.get_parameter("hold_time").value

        if wp_raw == "default":
            self.points = [
                (0.0, 3.0),
                (2.0, 5.0),
                (-2.0, 4.0),
                (0.0, 6.0),
                (3.0, 3.0),
                (-3.0, 2.0),
                (0.0, 3.0),
            ]
        else:
            try:
                vals = [float(v) for v in wp_raw.split(",")]
                self.points = [(vals[i], vals[i+1]) for i in range(0, len(vals), 2)]
            except:
                self.points = [(0.0, 3.0)]

        self.idx = 0
        self.pub = self.create_publisher(Float32MultiArray, "/quad/reference", 10)
        self.timer = self.create_timer(self.hold_time, self.publish_ref)

    def publish_ref(self):
        x, z = self.points[self.idx]
        msg = Float32MultiArray()
        msg.data = [float(x), float(z)]
        self.pub.publish(msg)
        self.idx = (self.idx + 1) % len(self.points)


def main():
    rclpy.init()
    rclpy.spin(TrajectoryNode())
    rclpy.shutdown()