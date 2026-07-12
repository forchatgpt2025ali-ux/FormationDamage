import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QListWidget, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import all 5 fully-functional real scientific module pages
from gui.page_mechanical import MechanicalPage
from gui.page_chemical import ChemicalPage
from gui.page_biological import BiologicalPage
from gui.page_thermal import ThermalPage
from gui.page_optimization import OptimizationPage

# =============================================================================
# Main Window Application Controller
# =============================================================================
class MainWindow(QMainWindow):
    """
    The main shell window acting as the system layout orchestrator, 
    connecting sidebar navigation to the 5 distinct simulation pages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formation Damage App - Advanced Scientific Analysis")
        self.setMinimumSize(1300, 850)
        
        # Central widget and baseline horizontal layout structural definition
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- SIDEBAR NAVIGATION ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        
        # Apply distinct bold corporate styling font to navigation list
        sidebar_font = QFont()
        sidebar_font.setPointSize(11)
        sidebar_font.setBold(True)
        self.sidebar.setFont(sidebar_font)
        
        # Strict module cataloging names matching scientific assignments
        module_names = [
            "1. Mechanical Damage",
            "2. Chemical Damage",
            "3. Biological Damage",
            "4. Thermal Damage",
            "5. Filtration Optimization"
        ]
        self.sidebar.addItems(module_names)
        self.sidebar.setCurrentRow(0) # Standard application entry view
        
        # --- STACKED WIDGET CONTAINER (PAGES) ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(20, 20, 20, 20)
        
        # Instantiating all 5 real core functional pages
        self.page_mechanical = MechanicalPage()
        self.page_chemical = ChemicalPage()
        self.page_biological = BiologicalPage()
        self.page_thermal = ThermalPage()
        self.page_optimization = OptimizationPage()
        
        # Appending views into stacked structural manager in synchronized indexing sequence
        self.stacked_widget.addWidget(self.page_mechanical)  # Index 0
        self.stacked_widget.addWidget(self.page_chemical)    # Index 1
        self.stacked_widget.addWidget(self.page_biological)  # Index 2
        self.stacked_widget.addWidget(self.page_thermal)     # Index 3
        self.stacked_widget.addWidget(self.page_optimization) # Index 4
        
        # Binding sidebar programmatic switches to update stacked container viewport indices
        self.sidebar.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # --- ASSEMBLE FRAMEWORK ARRANGEMENT ---
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)