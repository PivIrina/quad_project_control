import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from collections import deque


class Visualizer(Node):

    def __init__(self):
        super().__init__("visualizer")

        self.x = 0.0
        self.z = 0.0
        self.xr = 0.0
        self.zr = 0.0
        self.u1 = 0.0
        self.u2 = 0.0

        self.x_hist = deque(maxlen=5000)
        self.z_hist = deque(maxlen=5000)
        self.xr_hist = deque(maxlen=5000)
        self.zr_hist = deque(maxlen=5000)
        self.u1_hist = deque(maxlen=5000)
        self.u2_hist = deque(maxlen=5000)
        self.t_hist = deque(maxlen=5000)
        self.ex_hist = deque(maxlen=5000)
        self.ez_hist = deque(maxlen=5000)

        self.create_subscription(Float32MultiArray, "/quad/state", self.state_cb, 10)
        self.create_subscription(Float32MultiArray, "/quad/reference", self.ref_cb, 10)
        self.create_subscription(Float32MultiArray, "/quad/control", self.ctrl_cb, 10)

        plt.ion()
        self.fig, self.axs = plt.subplots(3, 1, figsize=(10, 10))
        self.timer = self.create_timer(0.1, self.update_plot)

    def state_cb(self, msg):
        self.x = msg.data[0]
        self.z = msg.data[1]

    def ref_cb(self, msg):
        self.xr = msg.data[0]
        self.zr = msg.data[1]

    def ctrl_cb(self, msg):
        self.u1 = msg.data[0]
        self.u2 = msg.data[1]

    def update_plot(self):
        self.x_hist.append(self.x)
        self.z_hist.append(self.z)
        self.xr_hist.append(self.xr)
        self.zr_hist.append(self.zr)
        self.u1_hist.append(self.u1)
        self.u2_hist.append(self.u2)
        t = len(self.t_hist) * 0.1
        self.t_hist.append(t)
        self.ex_hist.append(self.xr - self.x)
        self.ez_hist.append(self.zr - self.z)

        for ax in self.axs:
            ax.clear()

        ax = self.axs[0]
        ax.axvline(-5, color="gray", linestyle="--", alpha=0.3)
        ax.axvline(5, color="gray", linestyle="--", alpha=0.3)
        ax.axhline(0, color="gray", linestyle="--", alpha=0.3)
        ax.axhline(10, color="gray", linestyle="--", alpha=0.3)
        if len(self.x_hist) > 1:
            ax.plot(list(self.x_hist), list(self.z_hist), 'b-', linewidth=1.0, alpha=0.5)
        if len(self.xr_hist) > 0:
            unique_x, unique_z = [], []
            prev = None
            for xr, zr in zip(self.xr_hist, self.zr_hist):
                if (xr, zr) != prev:
                    unique_x.append(xr)
                    unique_z.append(zr)
                    prev = (xr, zr)
            ax.plot(unique_x, unique_z, 'rx', markersize=10, markeredgewidth=2)
        ax.plot(self.x, self.z, 'bo', markersize=8)
        ax.set_xlim(-6, 6)
        ax.set_ylim(-0.5, 10.5)
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Z [m]")
        ax.set_title("Trajectory")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        ax = self.axs[1]
        t_arr = list(self.t_hist)
        ax.plot(t_arr, list(self.ex_hist), 'b-', linewidth=1.0, label="X error")
        ax.plot(t_arr, list(self.ez_hist), 'r-', linewidth=1.0, label="Z error")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_ylabel("Error [m]")
        ax.set_title("Tracking Error")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        if len(t_arr) > 0:
            ax.set_xlim(max(0, t_arr[-1] - 30), max(30, t_arr[-1]))

        ax = self.axs[2]
        t_arr = list(self.t_hist)
        u1 = list(self.u1_hist)
        u2 = list(self.u2_hist)
        t_u = t_arr[-len(u1):]
        ax.plot(t_u, u1, 'b-', linewidth=1.0, label="u1")
        ax.plot(t_u, u2, 'r-', linewidth=1.0, label="u2")
        ax.axhline(5.886, color="gray", linestyle=":", linewidth=0.8)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Thrust [N]")
        ax.set_title("Control Inputs")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_ylim(0, 14)
        if len(t_u) > 0:
            ax.set_xlim(max(0, t_u[-1] - 30), max(30, t_u[-1]))

        plt.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


def main():
    rclpy.init()
    node = Visualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        plt.close("all")
        node.destroy_node()
        rclpy.shutdown()