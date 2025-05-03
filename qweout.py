from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QSpinBox, QDoubleSpinBox, QGroupBox, QLineEdit, QSizePolicy
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Анализатор колебаний")
        MainWindow.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, MainWindow)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.canvas)

        self.control_panel = QWidget()
        self.control_layout = QHBoxLayout(self.control_panel)

        self.left_panel = QGroupBox("Параметры")
        self.left_layout = QVBoxLayout(self.left_panel)

        

        self.component_layout = QHBoxLayout()
        self.component_label = QLabel("Компонент:")
        self.component_combo = QComboBox()
        self.component_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.component_layout.addWidget(self.component_label)
        self.component_layout.addWidget(self.component_combo, 1)
        self.left_layout.addLayout(self.component_layout)

        self.time_step_layout = QHBoxLayout()
        self.time_step_label = QLabel("Шаг времени (фс):")
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.1, 10.0)
        self.time_step_spin.setValue(1.0)
        self.time_step_spin.setSingleStep(0.1)
        self.time_step_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.time_step_layout.addWidget(self.time_step_label)
        self.time_step_layout.addWidget(self.time_step_spin, 1)
        self.left_layout.addLayout(self.time_step_layout)

        self.freq_range_layout = QHBoxLayout()
        self.freq_range_label = QLabel("Диапазон частот (см⁻¹):")
        self.freq_min_spin = QSpinBox()
        self.freq_min_spin.setRange(0, 10000)
        self.freq_min_spin.setValue(0)
        self.freq_max_spin = QSpinBox()
        self.freq_max_spin.setRange(1, 10000)
        self.freq_max_spin.setValue(500)
        self.freq_min_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.freq_max_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.freq_range_layout.addWidget(self.freq_range_label)
        self.freq_range_layout.addWidget(self.freq_min_spin, 1)
        self.freq_range_layout.addWidget(QLabel("до"))
        self.freq_range_layout.addWidget(self.freq_max_spin, 1)
        self.left_layout.addLayout(self.freq_range_layout)

        self.color_layout = QHBoxLayout()
        self.color_label = QLabel("Цвет графика:")
        self.color_combo = QComboBox()
        self.color_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_combo, 1)
        self.left_layout.addLayout(self.color_layout)

        self.style_layout = QHBoxLayout()
        self.style_label = QLabel("Стиль графика:")
        self.style_combo = QComboBox()
        self.style_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.style_layout.addWidget(self.style_label)
        self.style_layout.addWidget(self.style_combo, 1)
        self.left_layout.addLayout(self.style_layout)

        self.dpi_layout = QHBoxLayout()
        self.dpi_label = QLabel("Качество (DPI):")
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(50, 1000)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dpi_layout.addWidget(self.dpi_label)
        self.dpi_layout.addWidget(self.dpi_spin, 1)
        self.left_layout.addLayout(self.dpi_layout)

        self.xlabel_input = QLineEdit("Частота (см⁻¹)")
        self.ylabel_input = QLineEdit("Интенсивность")
        self.xlabel_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ylabel_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.left_layout.addWidget(QLabel("Подпись оси X:"))
        self.left_layout.addWidget(self.xlabel_input)
        self.left_layout.addWidget(QLabel("Подпись оси Y:"))
        self.left_layout.addWidget(self.ylabel_input)

        self.null_freqs_input = QLineEdit()
        self.null_freqs_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.null_points_layout = QHBoxLayout()
        self.null_points_label = QLabel("Сколько точек обнулить в начале спектра:")
        self.null_points_spin = QSpinBox()
        self.null_points_spin.setRange(0, 10000)
        self.null_points_spin.setValue(1000)
        self.null_points_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.null_points_layout.addWidget(self.null_points_label)
        self.null_points_layout.addWidget(self.null_points_spin, 1)
        self.left_layout.addLayout(self.null_points_layout)

        self.window_layout = QHBoxLayout()
        self.window_label = QLabel("Оконная функция:")
        self.window_combo = QComboBox()
        self.window_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.window_layout.addWidget(self.window_label)
        self.window_layout.addWidget(self.window_combo, 1)
        self.left_layout.addLayout(self.window_layout)

        self.autocorr_button = QPushButton("Автокорреляция: ВЫКЛ")
        self.autocorr_button.setCheckable(True)
        self.autocorr_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.left_layout.addWidget(self.autocorr_button)

        self.right_panel = QGroupBox("Действия")
        self.right_layout = QVBoxLayout(self.right_panel)

        self.file_button = QPushButton("Загрузить файл с данными")
        self.file_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.right_layout.addWidget(self.file_button)

        self.save_button = QPushButton("Сохранить график")
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.right_layout.addWidget(self.save_button)

        self.control_layout.addWidget(self.left_panel)
        self.control_layout.addWidget(self.right_panel)
        self.main_layout.addWidget(self.control_panel)
