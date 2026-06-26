import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray

import math
import csv
import time


class MetricsNode(Node):

    def __init__(self):

        super().__init__("metrics")

        self.x = 0.0
        self.z = 0.0

        self.xr = 0.0
        self.zr = 0.0

        self.n = 0

        self.ex2_sum = 0.0
        self.ez2_sum = 0.0

        self.t0 = time.time()

        self.file = open("metrics.csv", "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "t",
            "ex",
            "ez",
            "rmse_x",
            "rmse_z"
        ])

        self.create_subscription(
            Float32MultiArray,
            "/quad/state",
            self.state_cb,
            10
        )

        self.create_subscription(
            Float32MultiArray,
            "/quad/reference",
            self.ref_cb,
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.compute
        )

        self.get_logger().info("Metrics node started")

    def state_cb(self, msg):

        self.x = msg.data[0]
        self.z = msg.data[1]

    def ref_cb(self, msg):

        self.xr = msg.data[0]
        self.zr = msg.data[1]

    def compute(self):

        ex = self.x - self.xr
        ez = self.z - self.zr

        self.n += 1

        self.ex2_sum += ex * ex
        self.ez2_sum += ez * ez

        rmse_x = math.sqrt(self.ex2_sum / self.n)
        rmse_z = math.sqrt(self.ez2_sum / self.n)

        t = time.time() - self.t0

        self.writer.writerow([
            t,
            ex,
            ez,
            rmse_x,
            rmse_z
        ])

        self.file.flush()

        if self.n % 20 == 0:

            self.get_logger().info(
                f"RMSE x={rmse_x:.3f}, z={rmse_z:.3f}"
            )


def main():

    rclpy.init()

    node = MetricsNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()