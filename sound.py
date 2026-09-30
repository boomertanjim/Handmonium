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

bellowsPressure = 1.0
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
        2: 0.60,
        3: 0.80,
        4: 0.40,
        5: 0.50,
        6: 0.20,
        7: 0.30,
        8: 0.16,
        9: 0.12,
        10: 0.10,
        11: 0.08,
        12: 0.07,
        13: 0.06,
        14: 0.05,
        15: 0.045,
        16: 0.04,
        17: 0.035,
        18: 0.03,
        19: 0.025,
        20: 0.02
    }

    for harmonic, amplitude in harmonics.items():
        wave += amplitude * np.sin(2 * np.pi * harmonic * t)

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
    try:
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
    try:
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

    for i in list(envelope):
        if i not in phase:
            continue
        t = (np.arange(frames) + phase[i]) / sample_rate
        # lfo = 1 + 0.003 * np.sin(2 * np.pi * 5 * t)

        freq = notes[i]

        current_pressure = bellowsPressure

        frequency = (
            freq + pitchDrift * (current_pressure - 1.0)
        )

        reed1 = harmonium_wave(frequency, t)
        reed2 = harmonium_wave(frequency * secondReedDetune, t)

        oscillator = (reed1 + reed2 * secondReedGain)

        oscillator = enclosure_filter(oscillator, frequency)

        env = create_envelope(i, frames)

        wave += oscillator * env * current_pressure * voice_gain

        phase[i] += frames

    wave *= master_gain

    wave = np.tanh(wave)

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