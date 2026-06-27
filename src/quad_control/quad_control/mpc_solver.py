import casadi as ca


class MPCController:

    def __init__(self, dt=0.1, N=15):
        self.dt = dt
        self.N = N
        self.m = 1.2
        self.g = 9.81
        self.I = 0.03
        self.l = 0.2
        self.k_theta = 3.0
        self.k_omega = 1.0
        self.hover = self.m * self.g / 2.0
        self._build_solver()

    def _build_solver(self):
        opt = ca.Opti()
        X = opt.variable(6, self.N + 1)
        U = opt.variable(2, self.N)

        self.opt = opt
        self.X = X
        self.U = U
        self.x0_param = opt.parameter(6)
        self.x_ref_param = opt.parameter(1)
        self.z_ref_param = opt.parameter(1)

        opt.subject_to(X[:, 0] == self.x0_param)

        for k in range(self.N):
            opt.set_initial(U[0, k], self.hover)
            opt.set_initial(U[1, k], self.hover)

        cost = 0

        for k in range(self.N):
            xk, zk, thk = X[0, k], X[1, k], X[2, k]
            vxk, vzk, omk = X[3, k], X[4, k], X[5, k]
            u1k, u2k = U[0, k], U[1, k]

            F = u1k + u2k
            M = self.l * (u2k - u1k)

            ax = -F * ca.sin(thk) / self.m
            az =  F * ca.cos(thk) / self.m - self.g
            alpha = (M - self.k_theta * thk - self.k_omega * omk) / self.I

            opt.subject_to(X[:, k+1] == ca.vertcat(
                xk + self.dt * vxk,
                zk + self.dt * vzk,
                thk + self.dt * omk,
                vxk + self.dt * ax,
                vzk + self.dt * az,
                omk + self.dt * alpha
            ))

            cost += 100 * (xk - self.x_ref_param)**2
            cost += 100 * (zk - self.z_ref_param)**2
            cost += 10 * thk**2
            cost += 0.01 * (u1k - self.hover)**2
            cost += 0.01 * (u2k - self.hover)**2

            opt.subject_to(u1k >= 0.5)
            opt.subject_to(u2k >= 0.5)
            opt.subject_to(u1k <= 13.0)
            opt.subject_to(u2k <= 13.0)

        cost += 500 * (X[0, self.N] - self.x_ref_param)**2
        cost += 500 * (X[1, self.N] - self.z_ref_param)**2

        opt.minimize(cost)
        opt.solver("ipopt", {
            "print_time": False,
            "ipopt": {"print_level": 0, "max_iter": 200, "tol": 1e-2, "warm_start_init_point": "yes"}
        })

    def solve(self, x, z, theta, vx, vz, omega, x_ref, z_ref):
        self.opt.set_value(self.x0_param, [x, z, theta, vx, vz, omega])
        self.opt.set_value(self.x_ref_param, x_ref)
        self.opt.set_value(self.z_ref_param, z_ref)

        try:
            sol = self.opt.solve()
            u1 = float(sol.value(self.U[0, 0]))
            u2 = float(sol.value(self.U[1, 0]))
            self.opt.set_initial(sol.value_variables())
            return max(0.5, min(u1, 13.0)), max(0.5, min(u2, 13.0))
        except:
            return self.hover, self.hover