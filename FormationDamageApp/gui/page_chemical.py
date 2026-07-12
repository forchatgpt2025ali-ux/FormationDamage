import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QDoubleSpinBox, QPushButton, 
                               QTextEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from gui.canvas import MplCanvas
from core.chemical import ChemicalHysteresisSolver

class ChemicalWorker(QThread):
    """Worker thread to run multiphase rel-perm hysteresis calculations safely in the background."""
    finished = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        solver = ChemicalHysteresisSolver(
            s_filtrate=self.params['s_filtrate'],
            swir=self.params['swir'],
            sor=self.params['sor'],
            n_w=self.params['n_w'],
            n_o=self.params['n_o'],
            krw0=self.params['krw0'],
            kro0=self.params['kro0'],
            rw=self.params['rw'],
            r_damage=self.params['r_damage'],
            re=self.params['re']
        )
        results = solver.calculate_hysteresis()
        self.finished.emit(results)

class ChemicalPage(QWidget):
    """UI Controller for the Chemical Damage & Phase Trapping Module."""
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
        
        # Group 1: Core Saturation Parameters
        sat_group = QGroupBox("Fluid Saturation Endpoints")
        sat_layout = QFormLayout(sat_group)
        
        self.spin_swir = QDoubleSpinBox()
        self.spin_swir.setRange(0.01, 0.5)
        self.spin_swir.setSingleStep(0.01)
        self.spin_swir.setValue(0.20)
        sat_layout.addRow("Irreducible Water Sat (Swir):", self.spin_swir)
        
        self.spin_sor = QDoubleSpinBox()
        self.spin_sor.setRange(0.01, 0.5)
        self.spin_sor.setSingleStep(0.01)
        self.spin_sor.setValue(0.25)
        sat_layout.addRow("Residual Oil Sat (Sor):", self.spin_sor)
        
        self.spin_s_filtrate = QDoubleSpinBox()
        self.spin_s_filtrate.setRange(0.0, 0.6)
        self.spin_s_filtrate.setSingleStep(0.01)
        self.spin_s_filtrate.setValue(0.35)
        sat_layout.addRow("Max Filtrate Saturation (S_f):", self.spin_s_filtrate)
        
        left_layout.addWidget(sat_group)
        
        # Group 2: Corey Relative Permeability Parameters
        perm_group = QGroupBox("Corey Relative Permeability Functions")
        perm_layout = QFormLayout(perm_group)
        
        self.spin_krw0 = QDoubleSpinBox()
        self.spin_krw0.setRange(0.05, 1.0)
        self.spin_krw0.setValue(0.30)
        perm_layout.addRow("Water Rel-Perm Endpoint (krw0):", self.spin_krw0)
        
        self.spin_kro0 = QDoubleSpinBox()
        self.spin_kro0.setRange(0.05, 1.0)
        self.spin_kro0.setValue(0.80)
        perm_layout.addRow("Oil Rel-Perm Endpoint (kro0):", self.spin_kro0)
        
        self.spin_nw = QDoubleSpinBox()
        self.spin_nw.setRange(1.0, 6.0)
        self.spin_nw.setValue(2.5)
        perm_layout.addRow("Water Corey Exponent (n_w):", self.spin_nw)
        
        self.spin_no = QDoubleSpinBox()
        self.spin_no.setRange(1.0, 6.0)
        self.spin_no.setValue(3.0)
        perm_layout.addRow("Oil Corey Exponent (n_o):", self.spin_no)
        
        left_layout.addWidget(perm_group)
        
        # Group 3: Wellbore Geometry for Hawkins Estimation
        geom_group = QGroupBox("Invasion Geometry")
        geom_layout = QFormLayout(geom_group)
        
        self.spin_rw = QDoubleSpinBox()
        self.spin_rw.setRange(0.05, 1.0)
        self.spin_rw.setValue(0.1)
        geom_layout.addRow("Wellbore Radius rw (m):", self.spin_rw)
        
        self.spin_rdam = QDoubleSpinBox()
        self.spin_rdam.setRange(0.1, 5.0)
        self.spin_rdam.setValue(1.5)
        geom_layout.addRow("Invaded Zone Radius r_d (m):", self.spin_rdam)
        
        self.spin_re = QDoubleSpinBox()
        self.spin_re.setRange(5.0, 1000.0)
        self.spin_re.setValue(15.0)
        geom_layout.addRow("External Reservoir re (m):", self.spin_re)
        
        left_layout.addWidget(geom_group)
        
        # Action Buttons
        self.btn_run = QPushButton("Run Hysteresis Analytics")
        self.btn_run.clicked.connect(self.start_analysis)
        left_layout.addWidget(self.btn_run)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(120)
        left_layout.addWidget(self.console)
        
        splitter.addWidget(left_widget)
        
        # --- RIGHT SIDE: SCIENTIFIC PLOTS ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.canvas = MplCanvas(self)
        right_layout.addWidget(self.canvas)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 800])
        
        self.worker = None

    def start_analysis(self):
        self.btn_run.setEnabled(False)
        self.console.setText("Computing Land Trapping & Rel-Perm Hysteresis... Please Wait.\n")
        
        params = {
            's_filtrate': self.spin_s_filtrate.value(),
            'swir': self.spin_swir.value(),
            'sor': self.spin_sor.value(),
            'n_w': self.spin_nw.value(),
            'n_o': self.spin_no.value(),
            'krw0': self.spin_krw0.value(),
            'kro0': self.spin_kro0.value(),
            'rw': self.spin_rw.value(),
            'r_damage': self.spin_rdam.value(),
            're': self.spin_re.value()
        }
        
        self.worker = ChemicalWorker(params)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.start()

    @Slot(dict)
    def on_analysis_finished(self, results):
        self.btn_run.setEnabled(True)
        
        sw = results['sw']
        krw_drain = results['krw_drainage']
        kro_drain = results['kro_drainage']
        krw_imb = results['krw_imbibition']
        s_trapped = results['s_trapped']
        k_ratio = results['k_ratio']
        skin_chem = results['skin_chemical']
        
        # Log results to Dashboard Console
        self.console.append("Hysteresis evaluation successfully completed.")
        self.console.append(f"Calculated Trapped Phase Saturation (S_gt): {s_trapped:.4f}")
        self.console.append(f"Relative Permeability Impairment Ratio (k_damaged/k_init): {k_ratio:.4f}")
        self.console.append(f"Resulting Phase Trapping Skin Factor S: {skin_chem:.4f}")
        
        # Update scientific plots
        self.canvas.axes.clear()
        self.canvas.axes.plot(sw, krw_drain, color='#005aa0', linewidth=2.0, label='krw (Primary Drainage)')
        self.canvas.axes.plot(sw, kro_drain, color='#0a0a0a', linewidth=2.0, linestyle='--', label='kro (Primary Drainage)')
        self.canvas.axes.plot(sw, krw_imb, color='#e056fd', linewidth=2.5, label='krw (Imbibition - Shifted)')
        
        # Highlight trapped phase blockage boundary line
        self.canvas.axes.axvline(x=self.spin_swir.value() + s_trapped, color='#d63031', linestyle=':', label='Trapped Phase Cut-off')
        
        self.canvas.axes.set_title("Relative Permeability Hysteresis & Phase Trapping Blockage")
        self.canvas.axes.set_xlabel("Water Saturation (Sw)")
        self.canvas.axes.set_ylabel("Relative Permeability (Fraction)")
        self.canvas.axes.legend(loc='upper right')
        self.canvas.axes.set_xlim([self.spin_swir.value() - 0.02, 1.0 - self.spin_sor.value() + 0.02])
        self.canvas.axes.grid(True, linestyle='--', alpha=0.7, color='#ababab')
        self.canvas.draw()