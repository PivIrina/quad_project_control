import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import time


class Replay:

    def __init__(self, file):
        self.df = pd.read_csv(file)
        self.i = 0
        self.playing = True
        self.speed = 1.0

        self.fig, self.axs = plt.subplots(2, 2, figsize=(10, 8))
        self.ax_traj = self.axs[0, 0]
        self.ax_state = self.axs[0, 1]
        self.ax_ctrl = self.axs[1, 0]
        self.ax_err = self.axs[1, 1]

        ax_play = plt.axes([0.7, 0.02, 0.1, 0.05])
        ax_speed = plt.axes([0.2, 0.02, 0.4, 0.03])
        self.btn_play = Button(ax_play, "Play/Pause")
        self.btn_play.on_clicked(self.toggle)
        self.slider = Slider(ax_speed, "Speed", 0.1, 3.0, valinit=1.0)
        self.slider.on_changed(self.set_speed)
        self.fig.suptitle("Quadrotor Flight Replay")
        plt.ion()

    def toggle(self, event):
        self.playing = not self.playing

    def set_speed(self, val):
        self.speed = val

    def update(self):
        if not self.playing:
            plt.pause(0.05)
            return
        if self.i >= len(self.df):
            return

        row = self.df.iloc[self.i]
        x, z = row["x"], row["z"]
        xr, zr = row["x_ref"], row["z_ref"]

        self.ax_traj.clear()
        self.ax_traj.plot(self.df["x"], self.df["z"], alpha=0.3)
        self.ax_traj.plot(self.df["x_ref"], self.df["z_ref"], "--")
        self.ax_traj.scatter(x, z, c="red")
        self.ax_traj.set_title("2D Flight")

        self.ax_state.clear()
        self.ax_state.plot(self.df["x"], label="x")
        self.ax_state.plot(self.df["z"], label="z")
        self.ax_state.legend()
        self.ax_state.set_title("State")

        self.ax_ctrl.clear()
        self.ax_ctrl.plot(self.df["u1"], label="u1")
        self.ax_ctrl.plot(self.df["u2"], label="u2")
        self.ax_ctrl.legend()
        self.ax_ctrl.set_title("Control")

        self.ax_err.clear()
        self.ax_err.plot(self.df["x"] - self.df["x_ref"], label="ex")
        self.ax_err.plot(self.df["z"] - self.df["z_ref"], label="ez")
        self.ax_err.legend()
        self.ax_err.set_title("Tracking error")

        plt.pause(0.001)
        self.i += int(self.speed)


replay = Replay("quad_log.csv")
while True:
    replay.update()
    time.sleep(0.03)