import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from quad_sim.wind_model import WindModel


class SimulatorNode(Node):

    def __init__(self):
        super().__init__("simulator")

        self.declare_parameter("wind_amplitude", 1.0)
        self.declare_parameter("wind_frequency", 0.5)

        wind_amp = self.get_parameter("wind_amplitude").value
        wind_freq = self.get_parameter("wind_frequency").value

        self.dt = 0.02
        self.t = 0.0
        self.m = 1.2
        self.g = 9.81
        self.I = 0.03
        self.l = 0.2
        self.k_theta = 3.0
        self.k_omega = 1.0
        self.x = 0.0
        self.z = 0.5
        self.theta = 0.0
        self.vx = 0.0
        self.vz = 0.0
        self.omega = 0.0
        self.u1 = 5.886
        self.u2 = 5.886

        self.wind = WindModel(amplitude=wind_amp, frequency=wind_freq)

        self.state_pub = self.create_publisher(Float32MultiArray, "/quad/state", 10)
        self.control_sub = self.create_subscription(Float32MultiArray, "/quad/control", self.control_callback, 10)
        self.timer = self.create_timer(self.dt, self.step)

    def control_callback(self, msg):
        self.u1 = float(msg.data[0])
        self.u2 = float(msg.data[1])

    def step(self):
        self.t += self.dt
        F = self.u1 + self.u2
        wind_force = self.wind.force(self.t)

        ax = (-F * math.sin(self.theta) + wind_force) / self.m
        az = (F * math.cos(self.theta) - self.m * self.g) / self.m
        M = self.l * (self.u2 - self.u1)
        alpha = (M - self.k_theta * self.theta - self.k_omega * self.omega) / self.I

        self.vx += ax * self.dt
        self.vz += az * self.dt
        self.omega += alpha * self.dt
        self.x += self.vx * self.dt
        self.z += self.vz * self.dt
        self.theta += self.omega * self.dt

        if self.x < -5.0:
            self.x = -4.5; self.vx = abs(self.vx) * 0.8; self.theta = 0.0; self.omega = 0.0
        if self.x > 5.0:
            self.x = 4.5; self.vx = -abs(self.vx) * 0.8; self.theta = 0.0; self.omega = 0.0
        if self.z < 0.0:
            self.z = 0.0; self.vz = abs(self.vz) * 0.5
        if self.z > 10.0:
            self.z = 10.0; self.vz = -abs(self.vz) * 0.5

        msg = Float32MultiArray()
        msg.data = [float(self.x), float(self.z), float(self.theta),
                    float(self.vx), float(self.vz), float(self.omega)]
        self.state_pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(SimulatorNode())
    rclpy.shutdown()