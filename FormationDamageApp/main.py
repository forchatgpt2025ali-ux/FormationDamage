import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from gui.main_window import MainWindow

def setup_light_high_contrast_theme(app: QApplication):
    """
    Applies a professional clean light engineering dashboard theme
    with distinct visual contrast for serious analytics.
    """
    app.setStyle("Fusion")
    palette = QPalette()
    
    # Define corporate-grade crisp light palette components
    bg_color = QColor('#f5f5f5')        # Soft gray window frame backdrop
    base_color = QColor('#ffffff')      # Perfect white for input zones
    text_dark = QColor('#0a0a0a')       # Deep near-black charcoal for clean readability
    accent_blue = QColor('#005aa0')     # Corporate industrial blue for buttons/highlights
    border_gray = QColor('#ababab')     # Balanced gray for gridlines and separation boundaries
    
    palette.setColor(QPalette.Window, bg_color)
    palette.setColor(QPalette.WindowText, text_dark)
    palette.setColor(QPalette.Base, base_color)
    palette.setColor(QPalette.AlternateBase, bg_color)
    palette.setColor(QPalette.ToolTipBase, base_color)
    palette.setColor(QPalette.ToolTipText, text_dark)
    palette.setColor(QPalette.Text, text_dark)
    palette.setColor(QPalette.Button, base_color)
    palette.setColor(QPalette.ButtonText, text_dark)
    palette.setColor(QPalette.BrightText, QColor('#e74c3c'))
    palette.setColor(QPalette.Link, accent_blue)
    palette.setColor(QPalette.Highlight, accent_blue)
    palette.setColor(QPalette.HighlightedText, base_color)
    
    app.setPalette(palette)
    
    # Advanced high-visibility QSS (Qt Style Sheets) layout
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            font-size: 11px;
            color: #005aa0;
            border: 1px solid #ababab;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 4px;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            border: 1px solid #ababab;
            border-radius: 4px;
            padding: 4px;
            background-color: #ffffff;
            color: #0a0a0a;
            selection-background-color: #005aa0;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1.5px solid #005aa0;
        }
        QPushButton {
            background-color: #005aa0;
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 4px;
            padding: 8px;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #004477;
        }
        QPushButton:pressed {
            background-color: #002d55;
        }
        QPushButton:disabled {
            background-color: #dcdcdc;
            color: #8c8c8c;
        }
        QListWidget {
            background-color: #ffffff;
            border-right: 1px solid #ababab;
            outline: 0;
        }
        QListWidget::item {
            padding: 14px;
            color: #555555;
            border-bottom: 1px solid #f0f0f0;
        }
        QListWidget::item:hover {
            background-color: #f0f7ff;
            color: #005aa0;
        }
        QListWidget::item:selected {
            background-color: #e0f0ff;
            color: #005aa0;
            border-left: 5px solid #005aa0;
        }
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #ababab;
            border-radius: 4px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            color: #222222;
        }
        QSplitter::handle {
            background-color: #ababab;
        }
    """)

if __name__ == "__main__":
    # Create application instance
    app = QApplication(sys.argv)
    
    # Apply global scientific high-contrast styling layout
    setup_light_high_contrast_theme(app)
    
    # Fire up the comprehensive multi-module simulation environment
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())