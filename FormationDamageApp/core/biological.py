import numpy as np

class BiologicalBiofilmSolver:
    """
    Core scientific solver for biofilm growth kinetics in porous media
    using coupled Monod differential equations and Kozeny-Carman permeability decline.
    """
    def __init__(self, x0=1.0, s0=50.0, mu_max=1.2, ks=5.0, 
                 yield_coeff=0.4, kd=0.05, k_initial=100.0, x_max=500.0):
        
        self.x0 = x0                  # Initial biomass concentration (mg/L)
        self.s0 = s0                  # Initial substrate concentration (mg/L)
        self.mu_max = mu_max          # Max specific growth rate (1/day)
        self.ks = ks                  # Half-velocity constant (mg/L)
        self.yield_coeff = yield_coeff # Biomass yield coefficient (mg/mg)
        self.kd = kd                  # Bacterial decay rate (1/day)
        self.k_initial = k_initial    # Initial permeability (mD)
        self.x_max = x_max            # Maximum theoretical plugging biomass density (mg/L)

    def solve_system(self, total_days=30, dt=0.01):
        """
        Integrates the Monod ODE system over time using a high-precision explicit forward scheme.
        """
        steps = int(total_days / dt)
        time_array = np.linspace(0, total_days, steps)
        
        biomass = np.zeros(steps)
        substrate = np.zeros(steps)
        
        # Set initial conditions
        biomass[0] = self.x0
        substrate[0] = self.s0
        
        for i in range(1, steps):
            x_curr = biomass[i-1]
            s_curr = substrate[i-1]
            
            # Monod kinetic growth rate evaluation
            mu = self.mu_max * s_curr / (self.ks + s_curr)
            
            # Differential changes
            dx = (mu - self.kd) * x_curr * dt
            ds = - (mu / self.yield_coeff) * x_curr * dt
            
            # Update and bound states logically to physical limits
            biomass[i] = max(x_curr + dx, 0.0)
            substrate[i] = max(s_curr + ds, 0.0)
            
        # Calculate permeability decline using Modified Kozeny-Carman equation
        plugging_fraction = np.clip(biomass / self.x_max, 0.0, 0.99)
        k_ratio = (1.0 - plugging_fraction) ** 3
        k_absolute = self.k_initial * k_ratio
        
        # Compute specific damage time threshold metrics (e.g., time to 50% damage)
        def get_time_to_damage(target_ratio):
            indices = np.where(k_ratio <= (1.0 - target_ratio))[0]
            return time_array[indices[0]] if len(indices) > 0 else -1.0

        t_25 = get_time_to_damage(0.25)
        t_50 = get_time_to_damage(0.50)
        t_75 = get_time_to_damage(0.75)
        
        return {
            "time": time_array,
            "biomass": biomass,
            "substrate": substrate,
            "k_ratio": k_ratio,
            "k_absolute": k_absolute,
            "t_25": t_25,
            "t_50": t_50,
            "t_75": t_75
        }