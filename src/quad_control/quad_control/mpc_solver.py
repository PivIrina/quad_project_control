class MPCController:
    def __init__(self, dt=0.2, N=10):
        self.dt = dt
        self.m = 1.2
        self.g = 9.81
        self.I = 0.03
        self.l = 0.2
        self.hover = self.m * self.g / 2.0
        self.integral_x = 0.0
        self.integral_z = 0.0

    def solve(self, x, z, theta, vx, vz, omega, x_ref, z_ref):
        err_x = x_ref - x
        err_z = z_ref - z

        if abs(x) > 4.5:
            self.integral_x = 0.0
            self.integral_z = 0.0

        self.integral_x += 0.01 * err_x
        self.integral_x = max(-3.0, min(self.integral_x, 3.0))
        if err_x * self.integral_x < 0:
            self.integral_x *= 0.9

        self.integral_z += 0.01 * err_z
        self.integral_z = max(-1.5, min(self.integral_z, 1.5))

        common = 4.0 * err_z - 3.0 * vz + self.integral_z
        diff = 2.5 * err_x - 3.0 * vx + self.integral_x
        damp = -2.0 * theta - 0.5 * omega
        max_diff = 6.0

        u1 = self.hover + common + diff + damp
        u2 = self.hover + common - diff - damp

        if u1 - u2 > max_diff:
            mid = (u1 + u2) / 2
            u1 = mid + max_diff/2
            u2 = mid - max_diff/2
        elif u2 - u1 > max_diff:
            mid = (u1 + u2) / 2
            u1 = mid - max_diff/2
            u2 = mid + max_diff/2

        u1 = max(0.5, min(u1, 13.0))
        u2 = max(0.5, min(u2, 13.0))
        return u1, u2