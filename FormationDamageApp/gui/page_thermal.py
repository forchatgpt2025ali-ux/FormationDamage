import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QDoubleSpinBox, QPushButton, 
                               QTextEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from gui.canvas import MplCanvas
from core.thermal import ThermalDamageSolver

class ThermalWorker(QThread):
    """Worker thread to run temperature-dependent fines migration models safely in the background."""
    finished = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        solver = ThermalDamageSolver(
            contact_angle_init=self.params['contact_angle_init'],
            fines_conc=self.params['fines_conc'],
            salinity_ppm=self.params['salinity_ppm'],
            rw=self.params['rw'],
            re=self.params['re'],
            h=self.params['h'],
            q_inj=self.params['q_inj']
        )
        results = solver.solve_thermal_profile(
            temp_well=self.params['temp_well'],
            temp_res=self.params['temp_res'],
            grid_points=100
        )
        self.finished.emit(results)

class ThermalPage(QWidget):
    """UI Controller for the Thermal Damage & Fines Migration Module."""
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
        
        # Group 1: Thermal Conditions
        thermal_group = QGroupBox("Thermal Boundaries & Wettability")
        thermal_layout = QFormLayout(thermal_group)
        
        self.spin_twell = QDoubleSpinBox()
        self.spin_twell.setRange(0.0, 100.0)
        self.spin_twell.setValue(25.0)
        thermal_layout.addRow("Injected Fluid Temp (C):", self.spin_twell)
        
        self.spin_tres = QDoubleSpinBox()
        self.spin_tres.setRange(40.0, 250.0)
        self.spin_tres.setValue(115.0)
        thermal_layout.addRow("Initial Reservoir Temp (C):", self.spin_tres)
        
        self.spin_theta = QDoubleSpinBox()
        self.spin_theta.setRange(0.0, 180.0)
        self.spin_theta.setValue(90.0)
        thermal_layout.addRow("Initial Contact Angle (deg):", self.spin_theta)
        
        left_layout.addWidget(thermal_group)
        
        # Group 2: Colloidal & Fines Properties
        fines_group = QGroupBox("Colloidal & Fines Settings")
        fines_layout = QFormLayout(fines_group)
        
        self.spin_fines = QDoubleSpinBox()
        self.spin_fines.setRange(0.0, 0.1)
        self.spin_fines.setDecimals(4)
        self.spin_fines.setSingleStep(0.001)
        self.spin_fines.setValue(0.015)
        fines_layout.addRow("Mobilizable Fines Vol (frac):", self.spin_fines)
        
        self.spin_salinity = QDoubleSpinBox()
        self.spin_salinity.setRange(100.0, 200000.0)
        self.spin_salinity.setSingleStep(500.0)
        self.spin_salinity.setValue(4000.0)
        fines_layout.addRow("Injection Water Salinity (ppm):", self.spin_salinity)
        
        left_layout.addWidget(fines_group)
        
        # Group 3: Hydraulics & Well Geometry
        hyd_group = QGroupBox("Well Hydraulics & Dimensions")
        hyd_layout = QFormLayout(hyd_group)
        
        self.spin_q = QDoubleSpinBox()
        self.spin_q.setRange(1.0, 5000.0)
        self.spin_q.setValue(120.0)
        hyd_layout.addRow("Water Injection Rate (m3/d):", self.spin_q)
        
        self.spin_rw = QDoubleSpinBox()
        self.spin_rw.setRange(0.05, 1.0)
        self.spin_rw.setValue(0.1)
        hyd_layout.addRow("Wellbore Radius rw (m):", self.spin_rw)
        
        self.spin_re = QDoubleSpinBox()
        self.spin_re.setRange(5.0, 1000.0)
        self.spin_re.setValue(15.0)
        hyd_layout.addRow("External Radius re (m):", self.spin_re)
        
        self.spin_h = QDoubleSpinBox()
        self.spin_h.setRange(0.1, 200.0)
        self.spin_h.setValue(10.0)
        hyd_layout.addRow("Net Pay Thickness h (m):", self.spin_h)
        
        left_layout.addWidget(hyd_group)
        
        # Execution Controls
        self.btn_run = QPushButton("Run Thermal Migration Simulation")
        self.btn_run.clicked.connect(self.start_thermal_simulation)
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

    def start_thermal_simulation(self):
        self.btn_run.setEnabled(False)
        self.console.setText("Solving Thermal Gradient & Fines Dislodgement Balance... Please Wait.\n")
        
        params = {
            'contact_angle_init': self.spin_theta.value(),
            'fines_conc': self.spin_fines.value(),
            'salinity_ppm': self.spin_salinity.value(),
            'rw': self.spin_rw.value(),
            're': self.spin_re.value(),
            'h': self.spin_h.value(),
            'q_inj': self.spin_q.value(),
            'temp_well': self.spin_twell.value(),
            'temp_res': self.spin_tres.value()
        }
        
        self.worker = ThermalWorker(params)
        self.worker.finished.connect(self.on_thermal_simulation_finished)
        self.worker.start()

    @Slot(dict)
    def on_thermal_simulation_finished(self, results):
        self.btn_run.setEnabled(True)
        
        r_arr = results['r']
        temp_profile = results['temperature']
        contact_angle = results['contact_angle']
        k_ratio = results['k_ratio']
        skin_thermal = results['skin_thermal']
        
        # Output detailed thermodynamic metrics to Dashboard Console
        self.console.append("Thermal simulation successfully evaluated.")
        self.console.append(f"Maximum Thermal Skin Factor S: {skin_thermal:.4f}")
        self.console.append(f"Minimum Contact Angle Shift: {np.min(contact_angle):.1f} deg (Increased Water-Wetness)")
        self.console.append(f"Critical Velocity Breach Zone Radius: {r_arr[np.where(k_ratio < 1.0)[0][-1] if len(np.where(k_ratio < 1.0)[0]) > 0 else 0]:.2f} meters")
        
        # Clear and update double Y-axis or clean split charts on canvas
        self.canvas.axes.clear()
        
        # Plot Permeability Decline Curve (Primary Axis)
        ax1 = self.canvas.axes
        ax1.plot(r_arr, k_ratio * 100, color='#d35400', linewidth=2.5, label='Permeability Retention (%)')
        ax1.set_xlabel("Radial Distance from Wellbore Center (m)")
        ax1.set_ylabel("Permeability Retention (% of k0)", color='#d35400')
        ax1.tick_params(axis='y', labelcolor='#d35400')
        ax1.set_xscale('log')
        
        # Instantiating a secondary twin axis for Temperature distribution profile
        ax2 = ax1.twinx()
        ax2.plot(r_arr, temp_profile, color='#2980b9', linewidth=2.0, linestyle='--', label='Temperature Front')
        ax2.set_ylabel("Temperature (°C)", color='#2980b9')
        ax2.tick_params(axis='y', labelcolor='#2980b9')
        
        ax1.set_title("Temperature Profile vs Fines Mobilization Pore Plugging Profile")
        ax1.grid(True, linestyle='--', alpha=0.5, color='#ababab')
        self.canvas.draw()