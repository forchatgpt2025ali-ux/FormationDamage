import numpy as np

class FiltrationOptimizer:
    """
    Core scientific solver for balancing surface facility expenses (CAPEX/OPEX) 
    against subsurface injectivity decline penalties to find the optimal filter micron rating.
    """
    def __init__(self, psd_mean=15.0, tss_ppm=45.0, q_inj=100.0,
                 cost_capex_base=25000.0, cost_opex_base=15.0, cost_damage_base=85000.0):
        
        self.psd_mean = psd_mean            # Mean particle size of suspended solids (microns)
        self.tss = tss_ppm                  # Suspended solids concentration (ppm)
        self.q_inj = q_inj                  # Injection rate (m3/day)
        self.cost_capex_base = cost_capex_base   # Base capital expenditure modifier ($)
        self.cost_opex_base = cost_opex_base     # Base operating cost modifier ($/day/m3)
        self.cost_damage_base = cost_damage_base # Economic penalty for 100% loss of injectivity ($)

    def evaluate_cost_curve(self, rating_min=1.0, rating_max=50.0, points=100):
        """
        Generates cost breakdown arrays across a spectrum of filter ratings 
        and locates the absolute mathematical minimum cost optimization point.
        """
        ratings = np.linspace(rating_min, rating_max, points)
        
        capex_arr = np.zeros(points)
        opex_arr = np.zeros(points)
        damage_arr = np.zeros(points)
        total_arr = np.zeros(points)
        
        for i, d_f in enumerate(ratings):
            # 1. CAPEX model: Finer filter ratings grow exponentially in capital expense
            capex_arr[i] = self.cost_capex_base * ((self.psd_mean / d_f) ** 1.3)
            
            # 2. OPEX model: Backwashing frequency increases for tight micron constraints
            opex_arr[i] = self.cost_opex_base * self.q_inj * ((self.psd_mean / d_f) ** 1.8)
            
            # 3. Subsurface Plugging Damage Model: Particles smaller than d_f escape capture
            # Fraction of passing solids simulated using an upper-bound efficiency shift
            passage_fraction = 1.0 - np.exp(-0.15 * d_f)
            damage_arr[i] = self.cost_damage_base * (self.tss / 10.0) * passage_fraction
            
            total_arr[i] = capex_arr[i] + opex_arr[i] + damage_arr[i]
            
        # Find absolute minimum cost coordination indices
        min_idx = np.argmin(total_arr)
        optimal_rating = ratings[min_idx]
        min_total_cost = total_arr[min_idx]
        
        return {
            "ratings": ratings,
            "capex": capex_arr,
            "opex": opex_arr,
            "damage": damage_arr,
            "total_cost": total_arr,
            "optimal_rating": optimal_rating,
            "min_total_cost": min_total_cost,
            "opt_capex": capex_arr[min_idx],
            "opt_opex": opex_arr[min_idx],
            "opt_damage": damage_arr[min_idx]
        }