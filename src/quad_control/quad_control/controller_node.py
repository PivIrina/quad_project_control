import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from quad_control.mpc_solver import MPCController


class ControllerNode(Node):
    def __init__(self):
        super().__init__("controller")
        self.dt = 0.02
        self.timer = self.create_timer(self.dt, self.control_loop)
        self.x_ref = 0.0
        self.z_ref = 3.0
        self.x = 0.0
        self.z = 0.5
        self.theta = 0.0
        self.vx = 0.0
        self.vz = 0.0
        self.omega = 0.0
        self.controller = MPCController()

        self.ref_sub = self.create_subscription(Float32MultiArray, "/quad/reference", self.ref_callback, 10)
        self.control_pub = self.create_publisher(Float32MultiArray, "/quad/control", 10)
        self.state_sub = self.create_subscription(Float32MultiArray, "/quad/state", self.state_callback, 10)

    def state_callback(self, msg):
        self.x = msg.data[0]
        self.z = msg.data[1]
        self.theta = msg.data[2]
        self.vx = msg.data[3]
        self.vz = msg.data[4]
        self.omega = msg.data[5]

    def ref_callback(self, msg):
        self.x_ref = msg.data[0]
        self.z_ref = msg.data[1]

    def control_loop(self):
        u1, u2 = self.controller.solve(
            self.x, self.z, self.theta, self.vx, self.vz, self.omega,
            self.x_ref, self.z_ref
        )
        control = Float32MultiArray()
        control.data = [float(u1), float(u2)]
        self.control_pub.publish(control)


def main():
    rclpy.init()
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()