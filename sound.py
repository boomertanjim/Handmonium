# from pynput import keyboard
import numpy as np
import sounddevice as sd

sample_rate = 44100
frequency = 50
duration = 2

def sin_wave(freq, duration, volume = 0.3):
    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        endpoint=False
    )

    wave = np.sin(2 * np.pi * freq * t)

    return wave * volume

wave = sin_wave(frequency, 2)
sd.play(wave, sample_rate)
sd.wait()