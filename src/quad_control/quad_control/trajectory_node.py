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
                self.points = [
                    (vals[i], vals[i+1]) for i in range(0, len(vals), 2)
                ]
            except:
                self.get_logger().error(f"Bad waypoints: {wp_raw}, using default")
                self.points = [(0.0, 3.0)]

        self.idx = 0
        self.pub = self.create_publisher(Float32MultiArray, "/quad/reference", 10)
        self.timer = self.create_timer(self.hold_time, self.publish_ref)

        self.get_logger().info(
            f"Trajectory: {len(self.points)} points, hold={self.hold_time}s"
        )
        for i, (x, z) in enumerate(self.points):
            self.get_logger().info(f"  #{i}: ({x:.0f}, {z:.0f})")

    def publish_ref(self):
        x, z = self.points[self.idx]
        msg = Float32MultiArray()
        msg.data = [float(x), float(z)]
        self.pub.publish(msg)
        self.get_logger().info(f"→ Target #{self.idx}: ({x:.0f}, {z:.0f})")
        self.idx = (self.idx + 1) % len(self.points)


def main():
    rclpy.init()
    node = TrajectoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()