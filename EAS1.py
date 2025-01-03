import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, StringVar, OptionMenu, Frame, Scale, HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# ==== Fungsi Generate Sinyal ====
def generate_signal(sensor_type, params):
    random_amplitude = random.uniform(0.5, 1.0)  # Amplitudo acak maksimal 1.0
    random_frequency = random.uniform(0.1, 2.0)  # Frekuensi acak tambahan
    t = np.linspace(0, 10, 500)

    if sensor_type in ["DHT21", "DHT22", "Webcam", "Light Sensor"]:
        threshold = params.get("threshold", 5.0)
        signal = np.array([random_amplitude if temp > threshold else 0 for temp in t])

    elif sensor_type == "Microphone":
        amplitude = params.get("amplitude", 1.0)
        frequency = params.get("frequency", 1.0) + random_frequency
        signal = amplitude * np.sin(2 * np.pi * frequency * t)

    else:
        signal, t = None, None

    return signal, t

# ==== Fungsi DFT ====
def DFT(x, sampling_frequency=1.0):
    N = len(x)
    X = []
    for k in range(N):
        X_k = 0
        for n in range(N):
            e = np.exp(-2j * np.pi * k * n / N)
            X_k += x[n] / e
        X.append(X_k)
    freq = np.fft.fftfreq(N, d=1 / sampling_frequency)
    return np.array(X), freq

# ==== GUI ====
class SignalApp:
    def __init__(self, master):
        self.master = master
        master.title("Signal Generator and Viewer")

        main_frame = Frame(master, padx=20, pady=20)
        main_frame.pack()

        Label(main_frame, text="Pilih Jenis Sensor:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.sensor_type = StringVar(value="DHT21")
        self.sensor_menu = OptionMenu(
            main_frame, self.sensor_type, 
            "DHT21", "DHT22", "Light Sensor", "Webcam", "Microphone", 
            command=self.update_plots
        )
        self.sensor_menu.grid(row=0, column=1, sticky="ew", pady=5)

        Label(main_frame, text="Amplitudo:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.amplitude_slider = Scale(main_frame, from_=0.1, to=10.0, resolution=0.1, orient=HORIZONTAL, length=200)
        self.amplitude_slider.set(1.0)
        self.amplitude_slider.grid(row=1, column=1, pady=5)
        self.amplitude_slider.bind("<Motion>", lambda event: self.update_plots())

        Label(main_frame, text="Frekuensi Sinyal:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.frequency_slider = Scale(main_frame, from_=0.1, to=10.0, resolution=0.1, orient=HORIZONTAL, length=200)
        self.frequency_slider.set(1.0)
        self.frequency_slider.grid(row=2, column=1, pady=5)
        self.frequency_slider.bind("<Motion>", lambda event: self.update_plots())

        Label(main_frame, text="Frekuensi DFT:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.dft_frequency_slider = Scale(main_frame, from_=1.0, to=100.0, resolution=1.0, orient=HORIZONTAL, length=200)
        self.dft_frequency_slider.set(10.0)
        self.dft_frequency_slider.grid(row=3, column=1, pady=5)
        self.dft_frequency_slider.bind("<Motion>", lambda event: self.update_plots())

        self.plot_frame = Frame(master)
        self.plot_frame.pack()

        self.figure, (self.ax_signal, self.ax_dft) = plt.subplots(2, 1, figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack()

        self.params = {}
        self.update_plots()

    def update_plots(self, *args):
        self.params['amplitude'] = self.amplitude_slider.get()
        self.params['frequency'] = self.frequency_slider.get()
        self.params['threshold'] = self.frequency_slider.get()  # Menggunakan frekuensi slider untuk threshold
        sensor_type = self.sensor_type.get()
        sampling_frequency = self.dft_frequency_slider.get()

        signal, t = generate_signal(sensor_type, self.params)

        self.ax_signal.clear()
        self.ax_dft.clear()

        if signal is not None:
            # Plot sinyal asli
            if t is not None:
                self.ax_signal.plot(t, signal, label=f"Sinyal {sensor_type}")
                self.ax_signal.set_xlabel("Waktu (s)")
            else:
                self.ax_signal.step(range(len(signal)), signal, label=f"Sinyal {sensor_type}", where="mid")
                self.ax_signal.set_xlabel("Sampel")
            self.ax_signal.set_title(f"Sinyal {sensor_type}")
            self.ax_signal.set_ylabel("Amplitudo")
            self.ax_signal.grid()
            self.ax_signal.legend()

            # Plot DFT
            dft_result, freq = DFT(signal, sampling_frequency)
            self.ax_dft.plot(freq[:len(freq)//2], np.abs(dft_result[:len(dft_result)//2]), label="Magnitude DFT")
            self.ax_dft.set_title("Hasil DFT")
            self.ax_dft.set_xlabel("Frekuensi (Hz)")
            self.ax_dft.set_ylabel("Magnitude")
            self.ax_dft.grid()
            self.ax_dft.legend()

        self.canvas.draw()

if __name__ == "__main__":
    root = Tk()
    app = SignalApp(root)
    root.mainloop()
