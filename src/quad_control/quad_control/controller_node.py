import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from quad_control.mpc_solver import MPCController


class ControllerNode(Node):

    def __init__(self):
        super().__init__("controller")
        self.timer = self.create_timer(0.1, self.control_loop)
        self.x_ref, self.z_ref = 0.0, 3.0
        self.x, self.z, self.theta = 0.0, 0.5, 0.0
        self.vx, self.vz, self.omega = 0.0, 0.0, 0.0
        self.mpc = MPCController(dt=0.1, N=15)

        self.ref_sub = self.create_subscription(Float32MultiArray, "/quad/reference", self.ref_callback, 10)
        self.control_pub = self.create_publisher(Float32MultiArray, "/quad/control", 10)
        self.state_sub = self.create_subscription(Float32MultiArray, "/quad/state", self.state_callback, 10)

    def state_callback(self, msg):
        self.x, self.z, self.theta = msg.data[0], msg.data[1], msg.data[2]
        self.vx, self.vz, self.omega = msg.data[3], msg.data[4], msg.data[5]

    def ref_callback(self, msg):
        self.x_ref, self.z_ref = msg.data[0], msg.data[1]

    def control_loop(self):
        u1, u2 = self.mpc.solve(self.x, self.z, self.theta, self.vx, self.vz, self.omega, self.x_ref, self.z_ref)
        msg = Float32MultiArray()
        msg.data = [float(u1), float(u2)]
        self.control_pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(ControllerNode())
    rclpy.shutdown()