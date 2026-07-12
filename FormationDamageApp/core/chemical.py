import numpy as np

class ChemicalHysteresisSolver:
    """
    Core scientific solver for multiphase relative permeability hysteresis 
    and phase trapping calculation based on Land's model.
    """
    def __init__(self, s_filtrate=0.35, swir=0.20, sor=0.25, 
                 n_w=2.5, n_o=3.0, krw0=0.3, kro0=0.8, rw=0.1, r_damage=1.5, re=15.0):
        
        self.s_filtrate = s_filtrate  # Maximum filtrate invasion saturation change
        self.swir = swir              # Irreducible water saturation
        self.sor = sor                # Residual oil saturation
        self.n_w = n_w                # Corey exponent for water
        self.n_o = n_o                # Corey exponent for oil
        self.krw0 = krw0              # Water relative permeability endpoint
        self.kro0 = kro0              # Oil relative permeability endpoint
        
        # Geometrical parameters for Skin estimation via Hawkins formula
        self.rw = rw
        self.r_damage = r_damage
        self.re = re

    def calculate_hysteresis(self):
        """
        Computes drainage, trapped phase saturation via Land's coefficient, 
        imbibition curves, and the resulting skin factor blockage.
        """
        # Generate full saturation profile matrix
        sw_space = np.linspace(self.swir, 1.0 - self.sor, 100)
        
        # 1. Primary Drainage Calculations (Normalized Saturation)
        sw_norm = np.clip((sw_space - self.swir) / (1.0 - self.swir - self.sor), 0.0, 1.0)
        krw_drainage = self.krw0 * (sw_norm ** self.n_w)
        kro_drainage = self.kro0 * ((1.0 - sw_norm) ** self.n_o)
        
        # 2. Land's Trapping Model Configuration
        s_max_nw = 1.0 - self.swir
        # Maximum possible trapped saturation bounded logically
        s_gt_max = min(self.s_filtrate * 1.2, 0.45) 
        
        # Land trapping constant definition
        if s_gt_max > 0:
            c_land = (1.0 / s_gt_max) - (1.0 / s_max_nw)
        else:
            c_land = 0.0
            
        # Trapped phase saturation from actual invasion exposure
        s_trapped = self.s_filtrate / (1.0 + c_land * self.s_filtrate)
        
        # 3. Imbibition (Production phase path shift due to trapped blockage)
        # Shifted dynamic range for normalized water saturation during imbibition
        denominator = 1.0 - self.swir - s_trapped - self.sor
        if denominator <= 0:
            denominator = 1e-5
            
        sw_eff = np.clip((sw_space - self.swir) / denominator, 0.0, 1.0)
        krw_imbibition = self.krw0 * (sw_eff ** self.n_w)
        
        # 4. Damage Factor and Chemical Phase Trapping Skin Estimation
        # Find index near the invaded filtrate frontal shock
        idx_invasion = np.argmin(np.abs(sw_space - (self.swir + self.s_filtrate)))
        
        krw_undamaged = max(krw_drainage[idx_invasion], 1e-5)
        krw_damaged = krw_imbibition[idx_invasion]
        
        # Dynamic ratio of relative permeability reduction
        k_ratio = krw_damaged / krw_undamaged
        k_ratio = np.clip(k_ratio, 0.01, 1.0)
        
        # Analytical integration of Hawkins skin across the damaged radius boundary zone
        skin_chemical = ((1.0 / k_ratio) - 1.0) * np.log(self.r_damage / self.rw)
        
        return {
            "sw": sw_space,
            "krw_drainage": krw_drainage,
            "kro_drainage": kro_drainage,
            "krw_imbibition": krw_imbibition,
            "s_trapped": s_trapped,
            "k_ratio": k_ratio,
            "skin_chemical": skin_chemical
        }