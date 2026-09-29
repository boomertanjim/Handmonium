# from pynput import keyboard
import numpy as np
import sounddevice as sd

sample_rate = 44100
frequency = 440
duration = 2

def adsr(
    duration, attack, decay, sustain, release):
    totalSamples = int(duration * sample_rate)

    attackSamples = int(attack * sample_rate)
    decaySamples = int(decay * sample_rate)
    releaseSamples = int(release * sample_rate)

    sustainSamples = (totalSamples - attackSamples - decaySamples - releaseSamples)

    attackCurve = np.linspace(
        0,
        1,
        attackSamples,
        endpoint=False
    )

    decayCurve = np.linspace(
            1,
            sustain,
            decaySamples,
            endpoint=False
        )

    sustainCurve = np.full(
        sustainSamples,
        sustain
    )

    releaseCurve = np.linspace(
            sustain,
            0,
            releaseSamples
        )

    envelope = np.concatenate([
        attackCurve,
        decayCurve,
        sustainCurve,
        releaseCurve
    ])

    return envelope


def sin_wave(freq, duration, volume = 0.3):
    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        endpoint=False
    )

    wave = np.sin(2 * np.pi * freq * t)

    return wave * volume

wave = sin_wave(frequency, 3)
envelope = adsr(3, 1, 0.5, 0.6, 1)
wave *= envelope
sd.play(wave, sample_rate)
sd.wait()