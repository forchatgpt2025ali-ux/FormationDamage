import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QDoubleSpinBox, QSpinBox, QPushButton, 
                               QTextEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtCore import Qt
from gui.canvas import MplCanvas
from core.mechanical import DeepBedFiltrationSolver

class SimulationWorker(QThread):
    """Worker thread to run the 1D Radial Implicit solver safely in the background."""
    finished = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        # Instantiate the core physics solver with UI parameters
        solver = DeepBedFiltrationSolver(
            grid_cells=self.params['grid_cells'],
            rw=self.params['rw'],
            re=self.params['re'],
            h=self.params['h'],
            phi0=self.params['phi0'],
            k0=self.params['k0'],
            q_inj=self.params['q_inj'],
            c_in_ppm=self.params['c_in_ppm'],
            lambda0=self.params['lambda0'],
            a_param=self.params['a_param'],
            sigma_max=self.params['sigma_max'],
            beta=self.params['beta'],
            n_exp=self.params['n_exp']
        )
        # Execute the implicit time-stepping algorithm
        results = solver.solve(
            t_max_days=self.params['t_max_days'],
            dt_days=self.params['dt_days']
        )
        self.finished.emit(results)

class MechanicalPage(QWidget):
    """UI Controller for the Mechanical Formation Damage Module."""
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
        
        # Group 1: Reservoir Parameters
        res_group = QGroupBox("Reservoir & Grid Geometry")
        res_layout = QFormLayout(res_group)
        
        self.spin_k0 = QDoubleSpinBox()
        self.spin_k0.setRange(0.1, 5000.0)
        self.spin_k0.setValue(150.0)
        res_layout.addRow("Initial Permeability (mD):", self.spin_k0)
        
        self.spin_phi0 = QDoubleSpinBox()
        self.spin_phi0.setRange(0.01, 0.45)
        self.spin_phi0.setSingleStep(0.01)
        self.spin_phi0.setValue(0.22)
        res_layout.addRow("Initial Porosity (frac):", self.spin_phi0)
        
        self.spin_rw = QDoubleSpinBox()
        self.spin_rw.setRange(0.05, 1.0)
        self.spin_rw.setValue(0.1)
        res_layout.addRow("Wellbore Radius rw (m):", self.spin_rw)
        
        self.spin_re = QDoubleSpinBox()
        self.spin_re.setRange(1.0, 1000.0)
        self.spin_re.setValue(15.0)
        res_layout.addRow("External Radius re (m):", self.spin_re)
        
        self.spin_h = QDoubleSpinBox()
        self.spin_h.setRange(0.1, 200.0)
        self.spin_h.setValue(12.0)
        res_layout.addRow("Net Pay Thickness h (m):", self.spin_h)
        
        self.spin_cells = QSpinBox()
        self.spin_cells.setRange(10, 500)
        self.spin_cells.setValue(80)
        res_layout.addRow("Grid Cells (Log-Space):", self.spin_cells)
        
        left_layout.addWidget(res_group)
        
        # Group 2: Kinetics & Impairment Parameters
        kin_group = QGroupBox("Deposition & Impairment Kinetics")
        kin_layout = QFormLayout(kin_group)
        
        self.spin_lambda0 = QDoubleSpinBox()
        self.spin_lambda0.setRange(0.0, 50.0)
        self.spin_lambda0.setValue(3.5)
        kin_layout.addRow("Filtration Coeff lambda0 (1/m):", self.spin_lambda0)
        
        self.spin_a = QDoubleSpinBox()
        self.spin_a.setRange(0.0, 10.0)
        self.spin_a.setValue(0.4)
        kin_layout.addRow("Ripening Parameter (a):", self.spin_a)
        
        self.spin_sigma_max = QDoubleSpinBox()
        self.spin_sigma_max.setRange(0.001, 0.3)
        self.spin_sigma_max.setSingleStep(0.005)
        self.spin_sigma_max.setValue(0.04)
        kin_layout.addRow("Max Specific Deposit (sigma_max):", self.spin_sigma_max)
        
        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(1.0, 50.0)
        self.spin_beta.setValue(12.0)
        kin_layout.addRow("Damage Blockage Coeff (beta):", self.spin_beta)
        
        self.spin_n = QDoubleSpinBox()
        self.spin_n.setRange(1.0, 5.0)
        self.spin_n.setValue(3.0)
        kin_layout.addRow("Kozeny-Carman Exponent (n):", self.spin_n)
        
        left_layout.addWidget(kin_group)
        
        # Group 3: Operational Controls
        ops_group = QGroupBox("Operational Parameters")
        ops_layout = QFormLayout(ops_group)
        
        self.spin_q = QDoubleSpinBox()
        self.spin_q.setRange(0.1, 5000.0)
        self.spin_q.setValue(65.0)
        ops_layout.addRow("Water Injection Rate (m3/d):", self.spin_q)
        
        self.spin_cin = QDoubleSpinBox()
        self.spin_cin.setRange(0.0, 2000.0)
        self.spin_cin.setValue(45.0)
        ops_layout.addRow("Injected TSS (ppm):", self.spin_cin)
        
        self.spin_tmax = QDoubleSpinBox()
        self.spin_tmax.setRange(0.1, 365.0)
        self.spin_tmax.setValue(15.0)
        ops_layout.addRow("Simulation Duration (days):", self.spin_tmax)
        
        self.spin_dt = QDoubleSpinBox()
        self.spin_dt.setRange(0.001, 5.0)
        self.spin_dt.setDecimals(3)
        self.spin_dt.setValue(0.05)
        ops_layout.addRow("Time Step dt (days):", self.spin_dt)
        
        left_layout.addWidget(ops_group)
        
        # Run Button & Console Console
        self.btn_run = QPushButton("Run Forward PDE Simulation")
        self.btn_run.clicked.connect(self.start_simulation)
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
        
        # Set dynamic balance sizing
        splitter.setSizes([450, 800])
        
        self.worker = None

    def start_simulation(self):
        """Extracts inputs, blocks UI inputs safely, and runs the QThread pipeline."""
        self.btn_run.setEnabled(False)
        self.console.setText("Initializing Implicit PDE Solver... Please Wait.\n")
        
        params = {
            'grid_cells': self.spin_cells.value(),
            'rw': self.spin_rw.value(),
            're': self.spin_re.value(),
            'h': self.spin_h.value(),
            'phi0': self.spin_phi0.value(),
            'k0': self.spin_k0.value(),
            'q_inj': self.spin_q.value(),
            'c_in_ppm': self.spin_cin.value(),
            'lambda0': self.spin_lambda0.value(),
            'a_param': self.spin_a.value(),
            'sigma_max': self.spin_sigma_max.value(),
            'beta': self.spin_beta.value(),
            'n_exp': self.spin_n.value(),
            't_max_days': self.spin_tmax.value(),
            'dt_days': self.spin_dt.value()
        }
        
        self.worker = SimulationWorker(params)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.start()

    @Slot(dict)
    def on_simulation_finished(self, results):
        """Processes numerical arrays returned from background worker thread and updates axes."""
        self.btn_run.setEnabled(True)
        
        time_arr = results['time']
        skin_arr = results['skin_history']
        r_arr = results['r']
        k_ratio = results['k_ratio_final']
        
        # Write high-precision final values to the integrated dashboard console
        final_skin = skin_arr[-1]
        self.console.append(f"Simulation Complete execution successfully.")
        self.console.append(f"Final Skin Factor S(t): {final_skin:.4f}")
        self.console.append(f"Near-Wellbore Permeability Damage: {k_ratio[0]*100:.2f}% of k0 remaining.")
        
        # Graph updates - Plotting the transient Evolution of Skin Factor over time
        self.canvas.axes.clear()
        self.canvas.axes.plot(time_arr, skin_arr, color='#005aa0', linewidth=2.5, label='Skin Factor S(t)')
        self.canvas.axes.set_title("Skin Factor Evolution due to Particulate Deep Bed Filtration")
        self.canvas.axes.set_xlabel("Time (Days)")
        self.canvas.axes.set_ylabel("Skin Factor (Dimensionless)")
        self.canvas.axes.legend(loc='upper left')
        self.canvas.axes.grid(True, linestyle='--', alpha=0.7, color='#ababab')
        self.canvas.draw()