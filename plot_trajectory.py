import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("quad_log.csv")

plt.figure()

plt.plot(df["x"], df["z"], label="trajectory")
plt.plot(df["x_ref"], df["z_ref"], "--", label="reference")

plt.xlabel("x")
plt.ylabel("z")
plt.legend()
plt.grid()

plt.title("Quadrotor 2D trajectory")

plt.show()