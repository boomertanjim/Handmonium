from pynput import keyboard
import numpy as np
import sounddevice as sd

sample_rate = 44100
voice_gain = 0.1
master_gain = 0.8

attack = 0.1
decay = 0.05

sustain = 0.9

release = 0.1

phase = {}
envelope = {}
keyHeld = []

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
                state = "decay"

        elif state == "decay":
            progress = position / (decay * sample_rate)

            level = 1.0 - ((1.0 - sustain) * progress)

            position += 1

            if position >= (decay * sample_rate):
                position = 0
                level = sustain
                state = "sustain"

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
        oscillator = np.sin(2 * np.pi * notes[i] * t)

        env = create_envelope(i, frames)

        wave += oscillator * env * voice_gain

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