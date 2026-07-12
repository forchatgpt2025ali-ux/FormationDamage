import numpy as np

class DeepBedFiltrationSolver:
    """
    1D Radial Implicit Upwind Finite-Difference Solver for Deep Bed Filtration.
    Solves the advection-deposition mass balance and updates dynamic permeability.
    """
    def __init__(self, grid_cells=100, rw=0.1, re=10.0, h=10.0, 
                 phi0=0.25, k0=100.0, q_inj=50.0, c_in_ppm=100.0,
                 lambda0=2.0, a_param=0.5, sigma_max=0.05, beta=10.0, n_exp=3.0):
        
        self.nr = grid_cells
        self.rw = rw
        self.re = re
        self.h = h
        
        # Logarithmic radial grid for high resolution near the wellbore
        self.r_edges = np.logspace(np.log10(rw), np.log10(re), self.nr + 1)
        self.r = (self.r_edges[:-1] + self.r_edges[1:]) / 2.0
        self.dr = np.diff(self.r_edges)
        
        self.phi0 = phi0
        self.k0 = k0
        self.lambda0 = lambda0
        self.a = a_param
        self.sigma_max = sigma_max
        self.beta = beta
        self.n_exp = n_exp
        
        # Operational Parameters
        self.q_inj = q_inj  # m^3/day
        self.c_in = c_in_ppm * 1e-6  # Volumetric fraction
        
        # Steady-state Darcy velocity profile v(r) = q / (2 * pi * r * h)
        self.v_darcy = self.q_inj / (2.0 * np.pi * self.r * self.h)
        
        # State Variables
        self.C = np.zeros(self.nr)       
        self.sigma = np.zeros(self.nr)   
        self.phi = np.full(self.nr, phi0) 
        self.k_ratio = np.ones(self.nr)  
        
    def solve(self, t_max_days, dt_days):
        """
        Executes the time-stepping implicit FD solver.
        """
        time_steps = int(t_max_days / dt_days)
        time_array = np.linspace(0, t_max_days, time_steps)
        
        skin_history = np.zeros(time_steps)
        sigma_history = np.zeros((time_steps, self.nr))
        k_history = np.zeros((time_steps, self.nr))
        
        for n in range(time_steps):
            C_new = np.zeros(self.nr)
            sigma_new = np.zeros(self.nr)
            
            # Boundary Condition at wellbore
            C_prev_cell = self.c_in
            
            for i in range(self.nr):
                # Dynamic filtration coefficient (Iwasaki formulation)
                lam = self.lambda0 * (1.0 + self.a * (self.sigma[i] / self.phi0)) * \
                      (1.0 - (self.sigma[i] / self.sigma_max))
                lam = max(lam, 0.0) 
                
                # Implicit Upwind discretized equation terms
                term_time = self.phi[i] / dt_days
                term_space = self.v_darcy[i] / self.dr[i]
                term_sink = lam * self.v_darcy[i]
                
                # Solve for C_new[i]
                numerator = (term_time * self.C[i]) + (term_space * C_prev_cell)
                denominator = term_time + term_space + term_sink
                
                C_new[i] = numerator / denominator
                
                # Update specific deposit explicitly 
                d_sigma = lam * self.v_darcy[i] * C_new[i] * dt_days
                sigma_new[i] = min(self.sigma[i] + d_sigma, self.sigma_max * 0.99)
                
                C_prev_cell = C_new[i]
                
            # State Updates
            self.C = np.copy(C_new)
            self.sigma = np.copy(sigma_new)
            self.phi = self.phi0 - self.sigma
            
            # Permeability Impairment: Modified Kozeny-Carman
            self.k_ratio = (1.0 - self.beta * (self.sigma / self.phi0)) ** self.n_exp
            self.k_ratio = np.clip(self.k_ratio, 1e-5, 1.0)
            
            # Hawkins Skin Factor Integration
            integrand = (1.0 / self.k_ratio - 1.0) / self.r
            skin = np.sum(integrand * self.dr)
            
            skin_history[n] = skin
            sigma_history[n, :] = self.sigma
            k_history[n, :] = self.k_ratio
            
        return {
            "time": time_array,
            "r": self.r,
            "skin_history": skin_history,
            "sigma_final": self.sigma,
            "k_ratio_final": self.k_ratio,
            "k_history": k_history
        }