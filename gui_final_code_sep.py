import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
                             QHBoxLayout, QSlider, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AmmoniaAbsorptionGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Optimized Ammonia Recovery')
        self.setWindowIcon(QIcon('ammonia_icon.png'))
        self.setGeometry(200, 200, 1000, 700)

        self.setStyleSheet("""
            QWidget {
                background-color: #2d004d;
                color: #e0e0ff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ff00aa;
                color: white;
                border: 2px solid #ff66cc;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #cc0099;
            }
            QLabel {
                color: #c2f0f7;
                font-size: 15px;
            }
            QTabWidget::pane {
                border: 2px solid #5d00b3;
                background: #1f0033;
            }
            QTabBar::tab {
                background: #5d00b3;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #330066;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #9900cc;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 10px;
                background: #400080;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #ff00aa;
                border: 1px solid #ff66cc;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::add-page:horizontal {
                background: #330066;
            }
            QSlider::sub-page:horizontal {
                background: #9900cc;
            }
            QTabWidget QWidget {
                background-color: #1f0033;
            }
        """)

        self.layout = QVBoxLayout()

        self.title_label = QLabel('<b>Optimized Ammonia Recovery Process</b>', self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        self.layout.addWidget(self.title_label)

        self.description_label = QLabel('Select a CSV Dataset for Analysis:')
        self.layout.addWidget(self.description_label)

        self.load_button = QPushButton('Load Dataset', self)
        self.load_button.clicked.connect(self.load_dataset)
        self.layout.addWidget(self.load_button)

        self.status_label = QLabel('')
        self.layout.addWidget(self.status_label)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.df = None
        self.model = None
        self.X_test = None
        self.y_test = None
        self.y_pred = None
        self.metrics_label = None
        self.pH = 7.5  # Default pH

    def nh3_fraction(self, pH, pKa=9.25):
        return 1 / (1 + 10**(pKa - pH))

    def load_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

        if file_path:
            self.status_label.setText(f'Loaded Dataset: {file_path}')
            self.df = pd.read_csv(file_path)
            self.df['Time'] = np.arange(len(self.df))
            self.run_analysis()
            self.setup_mass_transfer_tabs()

    def run_analysis(self):
        X = self.df[['Time']]
        y = self.df['Ammonia']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        self.model.fit(X_train, y_train)

        self.y_pred = self.model.predict(X_test)
        self.X_test = X_test
        self.y_test = y_test

        mse = mean_squared_error(y_test, self.y_pred)
        r2 = r2_score(y_test, self.y_pred)
        mae = mean_absolute_error(y_test, self.y_pred)

        self.metrics_text = f"RandomForest Metrics:\nR2: {r2:.4f}\nMSE: {mse:.4f}\nMAE: {mae:.4f}"
        print(self.metrics_text)

        self.setup_model_evaluation_tab()

    def setup_model_evaluation_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        canvas = FigureCanvas(plt.figure(figsize=(10, 8)))
        fig = canvas.figure

        ax1 = fig.add_subplot(131)
        ax1.scatter(self.y_test, self.y_pred, alpha=0.6, color='orange')
        ax1.set_xlabel("Actual")
        ax1.set_ylabel("Predicted")
        ax1.set_title("Actual vs Predicted")

        ax2 = fig.add_subplot(132)
        residuals = self.y_test - self.y_pred
        ax2.scatter(self.y_test, residuals, color='purple', alpha=0.6)
        ax2.axhline(0, color='black', linestyle='--')
        ax2.set_title("Residual Plot")

        ax3 = fig.add_subplot(133)
        ax3.hist(residuals, bins=30, color='blue', alpha=0.7)
        ax3.set_title("Prediction Error Distribution")

        fig.tight_layout()
        layout.addWidget(canvas)

        self.metrics_label = QLabel(self.metrics_text)
        layout.addWidget(self.metrics_label)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Model Evaluation")

    def setup_mass_transfer_tabs(self):
        self.membrane_tab = QWidget()
        membrane_layout = QVBoxLayout()
        self.canvas_membrane = FigureCanvas(plt.figure(figsize=(10, 5)))
        membrane_layout.addWidget(self.canvas_membrane)
        self.membrane_tab.setLayout(membrane_layout)
        self.tabs.addTab(self.membrane_tab, "Membrane Flux")

        self.abs_strip_tab = QWidget()
        abs_strip_layout = QVBoxLayout()
        self.canvas_abs_strip = FigureCanvas(plt.figure(figsize=(10, 5)))
        abs_strip_layout.addWidget(self.canvas_abs_strip)
        self.abs_strip_tab.setLayout(abs_strip_layout)
        self.tabs.addTab(self.abs_strip_tab, "Absorption & Stripping")

        slider_widget = QWidget()
        slider_layout = QHBoxLayout()

        self.k_g_slider = QSlider(Qt.Horizontal)
        self.k_g_slider.setMinimum(1)
        self.k_g_slider.setMaximum(30)
        self.k_g_slider.setValue(10)
        self.k_g_slider.valueChanged.connect(self.update_mass_transfer_plot)
        slider_layout.addWidget(QLabel('k_G (mol/m²·s·Pa):'))
        slider_layout.addWidget(self.k_g_slider)

        self.k_l_slider = QSlider(Qt.Horizontal)
        self.k_l_slider.setMinimum(1)
        self.k_l_slider.setMaximum(20)
        self.k_l_slider.setValue(5)
        self.k_l_slider.valueChanged.connect(self.update_mass_transfer_plot)
        slider_layout.addWidget(QLabel('k_L (mol/m²·s·Pa):'))
        slider_layout.addWidget(self.k_l_slider)

        self.p_a_slider = QSlider(Qt.Horizontal)
        self.p_a_slider.setMinimum(1)
        self.p_a_slider.setMaximum(30)
        self.p_a_slider.setValue(10)
        self.p_a_slider.valueChanged.connect(self.update_mass_transfer_plot)
        slider_layout.addWidget(QLabel('P_A (mol/m²·s):'))
        slider_layout.addWidget(self.p_a_slider)

        self.ph_slider = QSlider(Qt.Horizontal)
        self.ph_slider.setMinimum(50)
        self.ph_slider.setMaximum(110)
        self.ph_slider.setValue(75)
        self.ph_slider.valueChanged.connect(self.update_mass_transfer_plot)
        slider_layout.addWidget(QLabel('pH:'))
        slider_layout.addWidget(self.ph_slider)

        slider_widget.setLayout(slider_layout)
        self.layout.addWidget(slider_widget)

        self.update_mass_transfer_plot()

    def update_mass_transfer_plot(self):
        if self.df is None:
            return

        k_g = self.k_g_slider.value() / 1000
        k_l = self.k_l_slider.value() / 1000
        p_a = self.p_a_slider.value() / 1000
        self.pH = self.ph_slider.value() / 10

        nh3_frac = self.nh3_fraction(self.pH)
        nh3_available = self.df['Ammonia'] * nh3_frac

        absorption_rate = k_g * (nh3_available - 0.034)
        stripping_rate = k_l * (nh3_available - 0.034)
        membrane_flux = (p_a * nh3_available) / 0.001

        self.canvas_abs_strip.figure.clear()
        ax1 = self.canvas_abs_strip.figure.add_subplot(111)
        ax1.plot(self.df['Time'], absorption_rate, label=f'Absorption (k_G={k_g:.3f})', color='blue')
        ax1.plot(self.df['Time'], stripping_rate, label=f'Stripping (k_L={k_l:.3f})', color='green')
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Rate")
        ax1.set_title(f"Absorption & Stripping vs Time (pH={self.pH})")
        ax1.legend()
        ax1.grid()
        self.canvas_abs_strip.draw()

        self.canvas_membrane.figure.clear()
        ax2 = self.canvas_membrane.figure.add_subplot(111)
        ax2.plot(self.df['Time'], membrane_flux, label=f'Membrane Flux (P_A={p_a:.1e})', color='red')
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Flux")
        ax2.set_title(f"Membrane Flux vs Time (pH={self.pH})")
        ax2.legend()
        ax2.grid()
        self.canvas_membrane.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AmmoniaAbsorptionGUI()
    window.show()
    sys.exit(app.exec_())