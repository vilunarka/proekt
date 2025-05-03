import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
from qweout import Ui_MainWindow
import matplotlib.pyplot as plt


class SpectralAnalyzer(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data = None
        self.autocorr_enabled = False

        # Инициализация значений по умолчанию
        self.time_step_spin.setValue(1.0)
        self.freq_min_spin.setRange(0, 10000)
        self.freq_min_spin.setValue(0)
        self.freq_max_spin.setRange(0, 10000)
        self.freq_max_spin.setValue(100)
        self.null_points_spin.setValue(0)
        
        # Заполнение выпадающих списков
        self.component_combo.addItems(["x-компонент", "y-компонент", "z-компонент", "Модуль"])
        self.color_combo.addItems(["blue", "red", "green", "black", "magenta", "cyan", "yellow", "purple"])
        self.window_combo.addItems(["None", "Hann", "Hamming", "Blackman"])
        self.style_combo.addItems(["Линия", "Точки", "Шаги", "Столбцы"])
        
        # Подписи осей
        self.xlabel_input.setText("Частота (см⁻¹)")
        self.ylabel_input.setText("Интенсивность")

        # Подключение сигналов
        self.file_button.clicked.connect(self.load_data)
        self.save_button.clicked.connect(self.save_plot)
        self.autocorr_button.clicked.connect(self.toggle_autocorrelation)
        
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
            self.style_combo.currentIndexChanged,
            self.xlabel_input.textChanged,
            self.ylabel_input.textChanged,
            self.null_freqs_input.textChanged,
            self.dpi_spin.valueChanged
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
        self.autocorr_button.setText("Автокорреляция: ВКЛ" if checked else "Автокорреляция: ВЫКЛ")
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
            return

        try:
            component_idx = self.component_combo.currentIndex()
            time_step = self.time_step_spin.value() * 1e-15
            freq_min = self.freq_min_spin.value()
            freq_max = self.freq_max_spin.value()
            color = self.color_combo.currentText()
            null_count = self.null_points_spin.value()
            window_type = self.window_combo.currentText()
            plot_style = self.style_combo.currentText()

            signal = self.data[:, component_idx + 1].copy()
            signal -= np.mean(signal)

            if window_type != "None":
                window = getattr(np, window_type.lower())(len(signal))
                signal *= window

            if self.autocorr_enabled:
                signal = self.compute_autocorrelation(signal)

            N = len(signal)
            fft_vals = np.abs(fft(signal)[:N//2])
            freqs = fftfreq(N, time_step)[:N//2] / 2.99792458e10
            
            if null_count > 0:
                fft_vals[:null_count] = 0

            # Обнуление указанных частот
            null_freqs_text = self.null_freqs_input.text().strip()
            if null_freqs_text:
                try:
                    null_freqs = [float(f) for f in null_freqs_text.split(',')]
                    for freq in null_freqs:
                        idx = np.abs(freqs - freq).argmin()
                        fft_vals[idx] = 0
                except:
                    pass

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            mask = (freqs >= freq_min) & (freqs <= freq_max)
            
            # Выбор стиля графика
            if plot_style == "Линия":
                ax.plot(freqs[mask], fft_vals[mask], color=color)
            elif plot_style == "Точки":
                ax.plot(freqs[mask], fft_vals[mask], 'o', color=color, markersize=2)
            elif plot_style == "Шаги":
                ax.step(freqs[mask], fft_vals[mask], color=color)
            elif plot_style == "Столбцы":
                width = (freq_max - freq_min) / len(freqs[mask]) * 0.8
                ax.bar(freqs[mask], fft_vals[mask], width=width, color=color, edgecolor=color)
            
            ax.set_title(f"Спектр {'(автокорр.)' if self.autocorr_enabled else ''}")
            ax.set_xlabel(self.xlabel_input.text())
            ax.set_ylabel(self.ylabel_input.text())
            ax.grid(True)
            
            self.canvas.draw()
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка: {str(e)}")

    def save_plot(self):
        if not hasattr(self, 'figure') or not self.figure.axes:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)"
        )

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