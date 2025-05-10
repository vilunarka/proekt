import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from qwerty import Ui_MainWindow
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class SpectralAnalyzer(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data = None
        self.autocorr_enabled = False

        # Инициализация значений по умолчанию
        self.time_step_spin.setValue(1)
        self.freq_min_spin.setRange(0, 10000)
        self.freq_min_spin.setValue(0)
        self.freq_max_spin.setRange(0, 10000)
        self.freq_max_spin.setValue(100)
        self.null_points_spin.setRange(0, 10000)  
        self.null_points_spin.setValue(0)
        
        # Graph init
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Заменяем QGraphicsView на наш canvas
        if self.widget.layout() is not None:
            QtWidgets.QWidget().setLayout(self.widget.layout()) 
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().addWidget(self.canvas) 

        # Заполнение выпадающих списков
        self.component_combo.addItems(["x-компонент", "y-компонент", "z-компонент", "Модуль"])
        self.color_combo.addItems(["blue", "red", "green", "black", "magenta", "purple"])
        self.window_combo.addItems(["None", "Hann", "Hamming", "Blackman"])
        
        # Подписи осей
        self.xlabel_input.setText("Частота (см⁻¹)")
        self.ylabel_input.setText("Интенсивность")

        # Подключение сигналов
        self.file_button.clicked.connect(self.load_data)
        self.save_button.clicked.connect(self.save_plot)
        self.autocorr_button.clicked.connect(self.toggle_autocorrelation)
        self.plt_btn.clicked.connect(self.plot_spectrum)
        
        # Подключение сигналов изменений параметров
        self.connect_parameter_signals()
        
    def connect_parameter_signals(self):
        """Подключает сигналы изменения параметров к обновлению графика"""
        signals = [
            self.component_combo.currentIndexChanged,
            self.time_step_spin.valueChanged,
            self.freq_min_spin.valueChanged,
            self.freq_max_spin.valueChanged,
            self.color_combo.currentIndexChanged,
            self.null_points_spin.valueChanged,
            self.window_combo.currentIndexChanged,
            self.xlabel_input.textChanged,
            self.ylabel_input.textChanged,
            self.dpi_spin.textChanged
        ]
        
        for signal in signals:
            signal.connect(self.schedule_plot_update)

    def schedule_plot_update(self):
        """Запланировать обновление графика с небольшой задержкой"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        else:
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.plot_spectrum)
        
        self.update_timer.start(300)  # 300 мс задержка

    def toggle_autocorrelation(self, checked):
        self.autocorr_enabled = checked
        self.autocorr_button.setText("ВКЛ" if checked else "ВЫКЛ")
        self.schedule_plot_update()

    def compute_autocorrelation(self, signal):
        autocorr = correlate(signal, signal, mode='same')
        return autocorr[len(autocorr)//4 : 3*len(autocorr)//4]

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с данными", "", 
            "Текстовые файлы (*.txt *.dat);;Все файлы (*)"
        )
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                if self.data.ndim == 1:
                    self.data = self.data.reshape(-1, 1)
                
                if self.data.shape[1] == 4:
                    time_step = self.time_step_spin.value()
                    time = np.arange(0, len(self.data) * time_step, time_step)
                    self.data = np.column_stack((time, self.data))
                
                self.statusBar().showMessage(f"Загружено {len(self.data)} точек")
                self.plot_spectrum()
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {str(e)}")
                self.data = None

    def plot_spectrum(self):
        if self.data is None:
            self.statusBar().showMessage("Ошибка: данные не загружены")
            return

        try:
            component_idx = self.component_combo.currentIndex()
            time_step = self.time_step_spin.value() * 1e-15
            color = self.color_combo.currentText()
            window_type = self.window_combo.currentText()

            signal = self.data[:, component_idx + 1].copy()
            signal -= np.mean(signal)

            if window_type != "None":
             if window_type == "Hann":
                window = np.hanning(len(signal))
             elif window_type == "Hamming":
                window = np.hamming(len(signal))
             elif window_type == "Blackman":
                window = np.blackman(len(signal))
             signal *= window

            if self.autocorr_enabled:
                signal = self.compute_autocorrelation(signal)

            N = len(signal)
            fft_vals = np.abs(fft(signal)[:N//2])
            fft_vals = fft_vals / np.max(fft_vals)
            freqs = fftfreq(N, time_step)[:N//2] / 2.99792458e10  # Переводим в см⁻¹
            
            null_count = self.null_points_spin.value()
            if null_count > 0:
                fft_vals = fft_vals.copy()  # Создаём копию для безопасности
                fft_vals[:null_count] = 0
            
            # Отладочный вывод
            print("Данные FFT:", fft_vals[:10])
            print("Частоты:", freqs[:10])

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(freqs, fft_vals, color=color)
            
            # Настройка осей
            ax.set_title(f"Спектр {'(автокорр.)' if self.autocorr_enabled else ''}")
            ax.set_xlabel(self.xlabel_input.text())
            ax.set_ylabel(self.ylabel_input.text())
            ax.grid(True)

            # Установка пределов, если заданы
            freq_min = self.freq_min_spin.value()
            freq_max = self.freq_max_spin.value()
            if freq_min < freq_max:
                ax.set_xlim(freq_min, freq_max)
            
            self.canvas.draw()
            self.statusBar().showMessage("График построен")
        
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка построения: {str(e)}")
            print("Ошибка в plot_spectrum:", str(e))

    def save_plot(self):
        if not hasattr(self, 'figure') or not self.figure.axes:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)")

        if file_path:
            try:
                dpi = self.dpi_spin.value()
                self.figure.savefig(file_path, dpi=dpi, bbox_inches='tight')
                self.statusBar().showMessage(f"Сохранено (DPI: {dpi})")
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpectralAnalyzer()
    window.show()
    sys.exit(app.exec_())