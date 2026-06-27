import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import csv
import time


class LoggerNode(Node):

    def __init__(self):
        super().__init__("logger")
        self.file = open("quad_log.csv", "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "t", "x", "z", "theta", "vx", "vz", "omega",
            "x_ref", "z_ref", "u1", "u2"
        ])
        self.state = None
        self.ref = None
        self.control = None
        self.t0 = time.time()

        self.create_subscription(Float32MultiArray, "/quad/state", self.state_cb, 10)
        self.create_subscription(Float32MultiArray, "/quad/reference", self.ref_cb, 10)
        self.create_subscription(Float32MultiArray, "/quad/control", self.control_cb, 10)
        self.timer = self.create_timer(0.1, self.log)

    def state_cb(self, msg):
        self.state = msg.data

    def ref_cb(self, msg):
        self.ref = msg.data

    def control_cb(self, msg):
        self.control = msg.data

    def log(self):
        if not (self.state and self.ref and self.control):
            return
        t = time.time() - self.t0
        self.writer.writerow([
            t,
            self.state[0], self.state[1], self.state[2],
            self.state[3], self.state[4], self.state[5],
            self.ref[0], self.ref[1],
            self.control[0], self.control[1]
        ])
        self.file.flush()


def main():
    rclpy.init()
    rclpy.spin(LoggerNode())
    rclpy.shutdown()