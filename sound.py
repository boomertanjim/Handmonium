# # def adsr(
# #     duration, attack, decay, sustain, release):
# #     totalSamples = int(duration * sample_rate)

# #     attackSamples = int(attack * sample_rate)
# #     decaySamples = int(decay * sample_rate)
# #     releaseSamples = int(release * sample_rate)

# #     sustainSamples = (totalSamples - attackSamples - decaySamples - releaseSamples)

# #     attackCurve = np.linspace(
# #         0,
# #         1,
# #         attackSamples,
# #         endpoint=False
# #     )

# #     decayCurve = np.linspace(
# #             1,
# #             sustain,
# #             decaySamples,
# #             endpoint=False
# #         )

# #     sustainCurve = np.full(
# #         sustainSamples,
# #         sustain
# #     )

# #     releaseCurve = np.linspace(
# #             sustain,
# #             0,
# #             releaseSamples
# #         )

# #     envelope = np.concatenate([
# #         attackCurve,
# #         decayCurve,
# #         sustainCurve,
# #         releaseCurve
# #     ])

# #     return envelope


# def sin_wave(freq, duration, volume = 0.3):
#     t = np.linspace(
#         0,
#         duration,
#         int(sample_rate * duration),
#         endpoint=False
#     )

#     wave = np.sin(2 * np.pi * freq * t)

#     return wave * volume




# # envelope = adsr(3, 1, 0.5, 0.6, 1)
# # wave *= envelope
# with keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release
# ) as listener:
#     listener.join()
#
#


from pynput import keyboard
import numpy as np
import sounddevice as sd

sample_rate = 44100

phase = 0
keyHeld = False

notes = {
    "a": 261.63,
    "s": 293.66,
    "d": 329.63,
    "e": 349.23,
    "f": 392.00,
    "g": 440.00,
    "h": 493.88,
    "j": 493.88,
    "k": 523.25
}

def on_press(key):
    global keyHeld
    try:
        if key.char == "s":
            keyHeld = True
        

    except AttributeError:
        pass

def on_release(key):
    global keyHeld
    try:
        if key.char == "s":
            keyHeld = False
    except AttributeError:
        if key == keyboard.Key.esc:
            return False

def audio_callback(outdata, frames, time, status):
    global phase

    t = (np.arange(frames) + phase) / sample_rate


    if keyHeld:
        wave = np.sin(
            2 * np.pi * 440 * t
        )
    else:
        wave = np.sin(
            2 * np.pi * 0 * t
        )


    outdata[:, 0] = wave

    phase += frames

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