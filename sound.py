from pynput import keyboard
import numpy as np
import sounddevice as sd

sample_rate = 44100
voice_gain = 0.15
master_gain = 1.2
attack = 0.07
decay = 0.0
sustain = 1.0
release = 0.2

phase = {}
envelope = {}
keyHeld = []

bellowsPressure = 0.0
pumpRate = 0.8
leakRate = 0.08
pumpHeld = False

pitchDrift = 0.8
secondReedGain = 0.18
secondReedDetune = 1.003

notes = {
    "a": 261.63,
    "s": 293.66,
    "d": 329.63,
    "f": 349.23,
    "g": 392.00,
    "h": 440.00,
    "j": 493.88,
    "k": 523.25
}

def harmonium_wave(freq, t):
    wave = np.zeros(len(t))

    harmonics = {
        1: 1.00,
        2: 0.75,
        3: 0.85,
        4: 0.55,
        5: 0.65,
        6: 0.35,
        7: 0.45,
        8: 0.28,
        9: 0.32,
        10: 0.20,
        11: 0.24,
        12: 0.15,
        13: 0.18,
        14: 0.12,
        15: 0.14,
        16: 0.09,
        17: 0.11,
        18: 0.07,
        19: 0.09,
        20: 0.05
    }

    for harmonic, amplitude in harmonics.items():
        wave += amplitude * np.sin(2 * np.pi * harmonic * freq * t)

    wave /= 3.95

    return wave

def enclosure_filter(wave, freq ):
    resonance1 = 1 + 0.12 * np.sin(
        2 * np.pi * 700 * np.arange(len(wave)) / sample_rate
    )

    resonance2 = 1 + 0.08 * np.sin(
        2 * np.pi * 1800 * np.arange(len(wave)) / sample_rate
    )

    wave = wave * resonance1 * resonance2

    return wave

def update_bellows(frames):
    global bellowsPressure

    dt = frames / sample_rate

    if pumpHeld:
        bellowsPressure += pumpRate * dt

    bellowsPressure -= leakRate * dt

    bellowsPressure = np.clip(
        bellowsPressure,
        0.0,
        1.0
    )

    return bellowsPressure

def create_envelope(note, frames):
    env = envelope[note]
    state = env["state"]
    position = env["position"]
    level = env["level"]

    output = np.zeros(frames)

    for i in range(frames):
        if state == "attack":
            level = position / (attack * sample_rate)

            position += 1

            if position >= (attack * sample_rate):
                position = 0
                level = 1.0
                state = "sustain"

        # elif state == "decay":
        #     progress = position / (decay * sample_rate)

        #     level = 1.0 - ((1.0 - sustain) * progress)

        #     position += 1

        #     if position >= (decay * sample_rate):
        #         position = 0
        #         level = sustain
        #         state = "sustain"

        elif state == "sustain":
            level = sustain

        elif state == "release":
            progress = position / (release * sample_rate)

            level = env["release_start"] * (1.0 - progress)

            position += 1

            if position >= (release * sample_rate):
                level = 0
                state = "finished"
        
        elif state == "finished":
            level = 0

        output[i] = level

    env["state"] = state
    env["position"] = position
    env["level"] = level

    return output

def on_press(key):
    global keyHeld
    global pumpHeld
    try:
        if key == keyboard.Key.space:
            pumpHeld = True
            return
        if key.char in notes:
            if key.char not in keyHeld:
                keyHeld.append(key.char)
                phase[key.char] = 0

                envelope[key.char] = {
                    "state": "attack",
                    "position": 0,
                    "level": 0,
                    "release_start": 0
                }
        

    except AttributeError:
        pass

def on_release(key):
    global keyHeld
    global pumpHeld
    try:
        if key == keyboard.Key.space:
            pumpHeld = False
            return
        if key.char in notes:
            if key.char in keyHeld:
                keyHeld.remove(key.char)
            if key.char in envelope:
                env = envelope[key.char]

                env["release_start"] = env["level"]
                env["state"] = "release"
                env["position"] = 0
    except AttributeError:
        if key == keyboard.Key.esc:
            return False

def audio_callback(outdata, frames, time, status):
    global phase
    wave = np.zeros(frames)
    current_pressure = update_bellows(frames)

    for i in list(envelope):
        if i not in phase:
            continue
        t = (np.arange(frames) + phase[i]) / sample_rate
        # lfo = 1 + 0.003 * np.sin(2 * np.pi * 5 * t)

        freq = notes[i]

        frequency = (
            freq + pitchDrift * (current_pressure - 0.7)
        )

        reedExcitation = current_pressure ** 1.5
        reed1 = harmonium_wave(frequency, t)
        reed1 = np.tanh(reed1 * (1.0 + current_pressure * 2.0))
        reed2 = harmonium_wave(frequency * secondReedDetune, t)
        reed2 = np.tanh(reed2 * (1.0 + current_pressure * 2.0))

        oscillator = (reed1 + reed2 * secondReedGain)

        # oscillator = enclosure_filter(oscillator, frequency)

        env = create_envelope(i, frames)

        wave += oscillator * env * reedExcitation * voice_gain

        phase[i] += frames

    wave *= master_gain

    outdata[:, 0] = wave

    for key in list(envelope):
        if envelope[key]["state"] == "finished":
            del envelope[key]
            del phase[key]

stream = sd.OutputStream(
    samplerate=sample_rate,
    channels=1,
    blocksize=128,
    callback=audio_callback
)

stream.start()
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

stream.stop()
stream.close()