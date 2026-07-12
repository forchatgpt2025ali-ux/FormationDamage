import numpy as np

class ThermalDamageSolver:
    """
    Core scientific solver for temperature-dependent wettability alteration,
    critical velocity evaluation, and subsequent clay fines migration damage.
    """
    def __init__(self, contact_angle_init=85.0, fines_conc=0.02, 
                 salinity_ppm=5000.0, rw=0.1, re=15.0, h=10.0, q_inj=80.0):
        
        self.theta_init = contact_angle_init # Initial contact angle (degrees)
        self.fines_conc = fines_conc         # Volumetric fraction of mobilizable fines
        self.salinity = salinity_ppm         # Water salinity (ppm)
        self.rw = rw
        self.re = re
        self.h = h
        self.q_inj = q_inj                   # Injection rate (m3/day)

    def solve_thermal_profile(self, temp_well=25.0, temp_res=110.0, grid_points=100):
        """
        Calculates radial temperature profile, wettability shift, 
        critical velocity threshold boundaries, and localized permeability reduction.
        """
        # Logarithmic grid for high-resolution radial investigation
        r_space = np.logspace(np.log10(self.rw), np.log10(self.re), grid_points)
        
        # Approximated steady-state thermal front profile between wellbore and reservoir
        temp_profile = temp_well + (temp_res - temp_well) * (np.log(r_space / self.rw) / np.log(self.re / self.rw))
        temp_profile = np.clip(temp_profile, temp_well, temp_res)
        
        # 1. Wettability Alteration: Linear-empirical thermal shift towards water-wet state
        # Higher temperatures reduce oil-wet stability flags
        beta_theta = 0.45  # Degrees Celsius shift coefficient
        contact_angle_evolved = self.theta_init - beta_theta * (temp_profile - temp_well)
        contact_angle_evolved = np.clip(contact_angle_evolved, 10.0, 150.0)
        
        # 2. Hydrodynamic Velocity Profile: v(r) = q / (2 * pi * r * h) in m/day
        velocity = self.q_inj / (2.0 * np.pi * r_space * self.h)
        
        # 3. Critical Velocity Formulation (Dependence on Salinity and Temperature)
        # Lower salinity and higher temperatures destabilize electrostatic double layers
        v_critical = (self.salinity / 10000.0) * (1.0 + 0.01 * (temp_profile - 25.0))
        v_critical = np.clip(v_critical, 0.1, 10.0) # Physical bounding
        
        # 4. Migration Tendency Index & Exponential Permeability Impairment
        migration_tendency = velocity / v_critical
        
        k_ratio = np.ones_like(r_space)
        for i in range(len(r_space)):
            if migration_tendency[i] > 1.0:
                # Fines mobilization triggered: Exponential pore throat choking
                severity = self.fines_conc * (migration_tendency[i] - 1.0)
                k_ratio[i] = np.exp(-120.0 * severity)
        
        k_ratio = np.clip(k_ratio, 0.02, 1.0)
        
        # Compute dynamic skin integration via Hawkins across the radial grid array
        dr = np.diff(r_space)
        dr = np.append(dr, dr[-1]) # Padding alignment
        integrand = (1.0 / k_ratio - 1.0) / r_space
        skin_thermal = np.sum(integrand * dr)
        
        return {
            "r": r_space,
            "temperature": temp_profile,
            "contact_angle": contact_angle_evolved,
            "migration_index": migration_tendency,
            "k_ratio": k_ratio,
            "skin_thermal": skin_thermal
        }