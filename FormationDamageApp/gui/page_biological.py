import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QDoubleSpinBox, QPushButton, 
                               QTextEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from gui.canvas import MplCanvas
from core.biological import BiologicalBiofilmSolver

class BioWorker(QThread):
    """Worker thread to run coupled Monod biofilm growth ODEs safely in the background."""
    finished = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        solver = BiologicalBiofilmSolver(
            x0=self.params['x0'],
            s0=self.params['s0'],
            mu_max=self.params['mu_max'],
            ks=self.params['ks'],
            yield_coeff=self.params['yield_coeff'],
            kd=self.params['kd'],
            k_initial=self.params['k_initial'],
            x_max=self.params['x_max']
        )
        results = solver.solve_system(
            total_days=self.params['total_days'],
            dt=self.params['dt']
        )
        self.finished.emit(results)

class BiologicalPage(QWidget):
    """UI Controller for the Biological Damage & Biofilm Growth Module."""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # --- LEFT SIDE: CONTROLS & INPUTS ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Group 1: Initial Microbial Conditions
        init_group = QGroupBox("Initial Microbial Concentration")
        init_layout = QFormLayout(init_group)
        
        self.spin_x0 = QDoubleSpinBox()
        self.spin_x0.setRange(0.01, 100.0)
        self.spin_x0.setValue(1.5)
        init_layout.addRow("Initial Biomass X0 (mg/L):", self.spin_x0)
        
        self.spin_s0 = QDoubleSpinBox()
        self.spin_s0.setRange(0.1, 1000.0)
        self.spin_s0.setValue(60.0)
        init_layout.addRow("Initial Substrate S0 (mg/L):", self.spin_s0)
        
        left_layout.addWidget(init_group)
        
        # Group 2: Monod Kinetic Coefficients
        kinetic_group = QGroupBox("Monod Kinetic Parameters")
        kinetic_layout = QFormLayout(kinetic_group)
        
        self.spin_mumax = QDoubleSpinBox()
        self.spin_mumax.setRange(0.1, 10.0)
        self.spin_mumax.setValue(1.4)
        kinetic_layout.addRow("Max Growth Rate mu_max (1/d):", self.spin_mumax)
        
        self.spin_ks = QDoubleSpinBox()
        self.spin_ks.setRange(0.1, 100.0)
        self.spin_ks.setValue(6.5)
        kinetic_layout.addRow("Half-Velocity Const Ks (mg/L):", self.spin_ks)
        
        self.spin_yield = QDoubleSpinBox()
        self.spin_yield.setRange(0.05, 0.95)
        self.spin_yield.setSingleStep(0.05)
        self.spin_yield.setValue(0.45)
        kinetic_layout.addRow("Biomass Yield Coeff (Y):", self.spin_yield)
        
        self.spin_kd = QDoubleSpinBox()
        self.spin_kd.setRange(0.0, 1.0)
        self.spin_kd.setSingleStep(0.01)
        self.spin_kd.setValue(0.06)
        kinetic_layout.addRow("Decay/Death Rate kd (1/d):", self.spin_kd)
        
        left_layout.addWidget(kinetic_group)
        
        # Group 3: Porous Media Plugging Parameters
        plug_group = QGroupBox("Porous Medium & Plugging Limits")
        plug_layout = QFormLayout(plug_group)
        
        self.spin_kinit = QDoubleSpinBox()
        self.spin_kinit.setRange(0.1, 5000.0)
        self.spin_kinit.setValue(120.0)
        plug_layout.addRow("Initial Permeability k0 (mD):", self.spin_kinit)
        
        self.spin_xmax = QDoubleSpinBox()
        self.spin_xmax.setRange(50.0, 5000.0)
        self.spin_xmax.setValue(600.0)
        plug_layout.addRow("Max Critical Biomass X_max (mg/L):", self.spin_xmax)
        
        left_layout.addWidget(plug_group)
        
        # Group 4: Grid and Time Stepping
        time_group = QGroupBox("Simulation Settings")
        time_layout = QFormLayout(time_group)
        
        self.spin_days = QDoubleSpinBox()
        self.spin_days.setRange(1.0, 365.0)
        self.spin_days.setValue(45.0)
        time_layout.addRow("Total Time (Days):", self.spin_days)
        
        self.spin_dt = QDoubleSpinBox()
        self.spin_dt.setRange(0.001, 1.0)
        self.spin_dt.setDecimals(3)
        self.spin_dt.setValue(0.01)
        time_layout.addRow("Time Step dt (Days):", self.spin_dt)
        
        left_layout.addWidget(time_group)
        
        # Execution Controls
        self.btn_run = QPushButton("Run Bio-Kinetic Simulation")
        self.btn_run.clicked.connect(self.start_bio_simulation)
        left_layout.addWidget(self.btn_run)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(120)
        left_layout.addWidget(self.console)
        
        splitter.addWidget(left_widget)
        
        # --- RIGHT SIDE: SCIENTIFIC CANVAS PLOT ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.canvas = MplCanvas(self)
        right_layout.addWidget(self.canvas)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 800])
        
        self.worker = None

    def start_bio_simulation(self):
        self.btn_run.setEnabled(False)
        self.console.setText("Executing Coupled Monod Biofilm Integrator... Please Wait.\n")
        
        params = {
            'x0': self.spin_x0.value(),
            's0': self.spin_s0.value(),
            'mu_max': self.spin_mumax.value(),
            'ks': self.spin_ks.value(),
            'yield_coeff': self.spin_yield.value(),
            'kd': self.spin_kd.value(),
            'k_initial': self.spin_kinit.value(),
            'x_max': self.spin_xmax.value(),
            'total_days': self.spin_days.value(),
            'dt': self.spin_dt.value()
        }
        
        self.worker = BioWorker(params)
        self.worker.finished.connect(self.on_bio_simulation_finished)
        self.worker.start()

    @Slot(dict)
    def on_bio_simulation_finished(self, results):
        self.btn_run.setEnabled(True)
        
        time_arr = results['time']
        biomass = results['biomass']
        k_ratio = results['k_ratio']
        
        t25, t50, t75 = results['t_25'], results['t_50'], results['t_75']
        
        # Output detailed operational metrics to Dashboard Console
        self.console.append("Biological simulation execution completed.")
        self.console.append(f"Peak Bacterial Biomass: {np.max(biomass):.2f} mg/L")
        self.console.append(f"Time to 25% Permeability Loss: {f'{t25:.2f} days' if t25 > 0 else 'N/A'}")
        self.console.append(f"Time to 50% Permeability Loss: {f'{t50:.2f} days' if t50 > 0 else 'N/A'}")
        self.console.append(f"Time to 75% Permeability Loss: {f'{t75:.2f} days' if t75 > 0 else 'N/A'}")
        
        # Clear and update double Y-axis or clean split charts on canvas
        self.canvas.axes.clear()
        
        # Plot Permeability Decline Curve (Primary Axis)
        ax1 = self.canvas.axes
        ax1.plot(time_arr, k_ratio * 100, color='#005aa0', linewidth=2.5, label='Permeability Retention (%)')
        ax1.set_xlabel("Time (Days)")
        ax1.set_ylabel("Permeability Retention (% of k0)", color='#005aa0')
        ax1.tick_params(axis='y', labelcolor='#005aa0')
        
        # Instantiating a secondary twin axis for Biomass Growth curves
        ax2 = ax1.twinx()
        ax2.plot(time_arr, biomass, color='#27ae60', linewidth=2.0, linestyle='--', label='Biomass Density')
        ax2.set_ylabel("Biomass Concentration (mg/L)", color='#27ae60')
        ax2.tick_params(axis='y', labelcolor='#27ae60')
        
        ax1.set_title("Biofilm Growth Kinetics & Dynamic Permeability Decline")
        ax1.grid(True, linestyle='--', alpha=0.5, color='#ababab')
        self.canvas.draw()