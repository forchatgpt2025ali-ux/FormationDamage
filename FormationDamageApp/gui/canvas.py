import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    """
    Standard embedded Matplotlib canvas configuring uniform aesthetic properties 
    across all engineering modules (High contrast, light theme layout).
    """
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # Apply professional crisp background to figure
        self.fig.patch.set_facecolor('#f5f5f5')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#ffffff')
        
        # Grid and axes typography styling
        self.axes.tick_params(colors='#0a0a0a', labelsize=10)
        self.axes.xaxis.label.set_color('#0a0a0a')
        self.axes.yaxis.label.set_color('#0a0a0a')
        self.axes.title.set_color('#005aa0')
        self.axes.title.set_fontweight('bold')
        
        # High-visibility background gridlines
        self.axes.grid(True, linestyle='--', alpha=0.7, color='#ababab')
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#555555')
            spine.set_linewidth(1.2)
            
        super().__init__(self.fig)
        self.setParent(parent)