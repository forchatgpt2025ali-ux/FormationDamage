import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QDoubleSpinBox, QPushButton, 
                               QTextEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from gui.canvas import MplCanvas
from core.optimization import FiltrationOptimizer

class OptWorker(QThread):
    """Worker thread to execute non-linear economic optimization functions safely in the background."""
    finished = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        optimizer = FiltrationOptimizer(
            psd_mean=self.params['psd_mean'],
            tss_ppm=self.params['tss_ppm'],
            q_inj=self.params['q_inj'],
            cost_capex_base=self.params['cost_capex_base'],
            cost_opex_base=self.params['cost_opex_base'],
            cost_damage_base=self.params['cost_damage_base']
        )
        results = optimizer.evaluate_cost_curve(
            rating_min=1.0,
            rating_max=60.0,
            points=120
        )
        self.finished.emit(results)

class OptimizationPage(QWidget):
    """UI Controller for the Filtration Design & Lifecycle Cost Optimization Module."""
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
        
        # Group 1: Particle Feed Characteristics
        feed_group = QGroupBox("Suspended Solids Information")
        feed_layout = QFormLayout(feed_group)
        
        self.spin_psd = QDoubleSpinBox()
        self.spin_psd.setRange(1.0, 100.0)
        self.spin_psd.setValue(18.0)
        feed_layout.addRow("Mean Particle Size (microns):", self.spin_psd)
        
        self.spin_tss = QDoubleSpinBox()
        self.spin_tss.setRange(0.1, 500.0)
        self.spin_tss.setValue(35.0)
        feed_layout.addRow("Feed TSS Concentration (ppm):", self.spin_tss)
        
        self.spin_q = QDoubleSpinBox()
        self.spin_q.setRange(10.0, 10000.0)
        self.spin_q.setValue(150.0)
        feed_layout.addRow("Water Injection Rate (m3/d):", self.spin_q)
        
        left_layout.addWidget(feed_group)
        
        # Group 2: CAPEX & OPEX Financial Drivers
        financial_group = QGroupBox("Surface Equipment Cost Drivers")
        financial_layout = QFormLayout(financial_group)
        
        self.spin_capex_base = QDoubleSpinBox()
        self.spin_capex_base.setRange(100.0, 1000000.0)
        self.spin_capex_base.setSingleStep(1000.0)
        self.spin_capex_base.setValue(30000.0)
        financial_layout.addRow("Base CAPEX Coeff ($):", self.spin_capex_base)
        
        self.spin_opex_base = QDoubleSpinBox()
        self.spin_opex_base.setRange(0.1, 500.0)
        self.spin_opex_base.setValue(18.5)
        financial_layout.addRow("Base OPEX Coeff ($/d/m3):", self.spin_opex_base)
        
        left_layout.addWidget(financial_group)
        
        # Group 3: Subsurface Reservoir Risk Drivers
        risk_group = QGroupBox("Subsurface Risk Penalty")
        risk_layout = QFormLayout(risk_group)
        
        self.spin_damage_base = QDoubleSpinBox()
        self.spin_damage_base.setRange(100.0, 5000000.0)
        self.spin_damage_base.setSingleStep(5000.0)
        self.spin_damage_base.setValue(95000.0)
        risk_layout.addRow("100% Injectivity Loss Cost ($):", self.spin_damage_base)
        
        left_layout.addWidget(risk_group)
        
        # Execution Controls
        self.btn_run = QPushButton("Execute Economic Optimization")
        self.btn_run.clicked.connect(self.start_optimization)
        left_layout.addWidget(self.btn_run)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(140)
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

    def start_optimization(self):
        self.btn_run.setEnabled(False)
        self.console.setText("Executing Non-Linear Cost Balancing Search... Please Wait.\n")
        
        params = {
            'psd_mean': self.spin_psd.value(),
            'tss_ppm': self.spin_tss.value(),
            'q_inj': self.spin_q.value(),
            'cost_capex_base': self.spin_capex_base.value(),
            'cost_opex_base': self.spin_opex_base.value(),
            'cost_damage_base': self.spin_damage_base.value()
        }
        
        self.worker = OptWorker(params)
        self.worker.finished.connect(self.on_optimization_finished)
        self.worker.start()

    @Slot(dict)
    def on_optimization_finished(self, results):
        self.btn_run.setEnabled(True)
        
        ratings = results['ratings']
        capex = results['capex']
        opex = results['opex']
        damage = results['damage']
        total_cost = results['total_cost']
        
        opt_rating = results['optimal_rating']
        min_total = results['min_total_cost']
        
        # Output optimized lifecycle costs inside Dashboard Console
        self.console.append("Economic Optimization Engine successfully converged.")
        self.console.append(f"Optimal Filter Micron Rating: {opt_rating:.2f} microns")
        self.console.append(f"Minimized Lifecycle Total Cost: ${min_total:,.2f}")
        self.console.append(f" -> Allocated CAPEX at Optimum: ${results['opt_capex']:,.2f}")
        self.console.append(f" -> Allocated OPEX at Optimum: ${results['opt_opex']:,.2f}")
        self.console.append(f" -> Allocated Formation Risk Penalty: ${results['opt_damage']:,.2f}")
        
        # Clear and render economic curve layouts on high-contrast canvas
        self.canvas.axes.clear()
        
        self.canvas.axes.plot(ratings, total_cost, color='#005aa0', linewidth=3.0, label='Total Lifecycle Cost')
        self.canvas.axes.plot(ratings, capex, color='#7f8c8d', linewidth=1.5, linestyle=':', label='Surface Facility CAPEX')
        self.canvas.axes.plot(ratings, opex, color='#27ae60', linewidth=1.5, linestyle='--', label='Operational OPEX')
        self.canvas.axes.plot(ratings, damage, color='#c0392b', linewidth=1.5, linestyle='-.', label='Formation Damage Penalty')
        
        # Drawing vertical guideline pointing straight to the calculated absolute optimal rating minimum
        self.canvas.axes.axvline(x=opt_rating, color='#d35400', linestyle='-', linewidth=2.0, 
                                 label=f"Optimal Target ({opt_rating:.2f} um)")
        self.canvas.axes.scatter(opt_rating, min_total, color='#d35400', s=80, zorder=5)
        
        self.canvas.axes.set_title("Filtration Cost Balancing: Surface Facility vs Subsurface Risk")
        self.canvas.axes.set_xlabel("Filter Rating Size Metric (Microns)")
        self.canvas.axes.set_ylabel("Lifecycle Financial Value Estimation ($)")
        self.canvas.axes.legend(loc='upper right')
        self.canvas.axes.grid(True, linestyle='--', alpha=0.5, color='#ababab')
        
        # Automatic scientific vertical zooming to keep visuals clear
        self.canvas.axes.set_ylim([0, np.percentile(total_cost, 85)])
        self.canvas.draw()