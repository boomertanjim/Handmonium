import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import numpy as np
import sounddevice as sd

baseOptions = python.BaseOptions(model_asset_path = "hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options = baseOptions,
                                       num_hands = 2)
detector = vision.HandLandmarker.create_from_options(options)

vid = cv.VideoCapture(0)

vid.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
vid.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
vid.set(cv.CAP_PROP_FPS, 30)


# Display Vars
cords = [
    [(), (), (), (), (), (), ()],
    [(), (), (), (), (), (), ()]
]
smoothDistances = [
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0]
]
smoothing = 0.25

touchCandidate = [
    [False, False, False, False],
    [False, False, False, False]
]

touchCounter = [
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

debounceFrames = 2

touch = [
    [False, False, False, False],[False, False, False, False]
]

# Audio Vars

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
targetPressure = 0.0
pressureSmoothing = 0.15

pitchDrift = 0.8
secondReedGain = 0.18
secondReedDetune = 1.003

notes = {
    "index0": 261.63,
    "middle0": 293.66,
    "ring0": 329.63,
    "pinky0": 349.23,
    "index1": 392.00,
    "middle1": 440.00,
    "ring1": 493.88,
    "pinky1": 523.25,

}

if not vid.isOpened():
    print("ERROR")
    exit()

image = mp.Image.create_from_file("image.jpg")

# Display Functions

def draw_landmarks_on_image(rgb_image, result):
    frame = rgb_image.copy()
    hand_landmarks_list = result.hand_landmarks

    for handLandmarks in hand_landmarks_list:
        connections = vision.HandLandmarksConnections.HAND_CONNECTIONS
        for connection in connections:
            start = handLandmarks[connection.start]
            end = handLandmarks[connection.end]

            startPoint = (
                int(start.x * frame.shape[1]),
                int(start.y * frame.shape[0])
            )

            endPoint = (
                int(end.x * frame.shape[1]),
                int(end.y * frame.shape[0])
            )

            cv.line(
                frame,
                startPoint,
                endPoint,
                (255, 0, 0),
                3
            )
        for landmark in handLandmarks:
            xCord = int(landmark.x * frame.shape[1])
            yCord = int(landmark.y * frame.shape[0])
            radius = int(14 * abs(landmark.z))

            cv.circle(
                frame,
                (xCord, yCord),
                radius,
                (0, 255, 0),
                10
            )


    return frame

def define_points (result):
    global cords

    cords = [
        [(), (), (), (), (), (), ()],
        [(), (), (), (), (), (), ()]
    ]

    hands = result.hand_landmarks
    handedness = result.handedness

    for handIndex, hand in enumerate(hands):

        label = handedness[handIndex][0].category_name

        if label == "Right":
            handSlot = 0
        else:
            handSlot = 1
        
        cords[handSlot][0] = (hand[4].x, hand[4].y)
        cords[handSlot][1] = (hand[8].x, hand[8].y)
        cords[handSlot][2] = (hand[12].x, hand[12].y)
        cords[handSlot][3] = (hand[16].x, hand[16].y)
        cords[handSlot][4] = (hand[20].x, hand[20].y)

        cords[handSlot][5] = (hand[0].x, hand[0].y)
        cords[handSlot][6] = (hand[9].x, hand[9].y)

def find_distance (a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def distance_Calc():
    ans = []

    for i in range(2):
        hand = []

        if not cords[i][0]:
            ans.append([0,0,0,0])
            continue

        thumb = cords[i][0]

        wrist = cords[i][5]
        middle_mcp = cords[i][6]

        handSize = find_distance(wrist, middle_mcp)

        if handSize == 0:
            ans.append([0, 0, 0, 0])
            continue

        for j in range (1, 5):
            fingerDistance = find_distance(thumb, cords[i][j])
            normalizedDistance = fingerDistance / handSize
            hand.append(normalizedDistance)

        ans.append(hand)

    return ans

def update_touch(distances):
    note_names = [
        ["index0", "middle0", "ring0","pinky0"],
        ["index1", "middle1", "ring1","pinky1"]
    ]

    touch_on = 0.25
    touch_off = 0.32

    for hand in range(2):
        for finger in range(4):
            note_name = note_names[hand][finger]
            distance = distances[hand][finger]

            # smoothDistances[hand][finger] += (
            #     distance - smoothDistances[hand][finger]
            # ) * smoothing

            # distance = smoothDistances[hand][finger]

            if not touch[hand][finger]:
                if distance > 0 and distance < touch_on:
                    touchCounter[hand][finger] += 1

                    if touchCounter[hand][finger] >= debounceFrames:
                        touch[hand][finger] = True
                        touchCounter[hand][finger] = 0
                        print("NOTE ON: ", note_name)
                        start_note(note_name)
                else:
                    touchCounter[hand][finger] = 0

            else:
                if distance == 0 or distance > touch_off:

                    touchCounter[hand][finger] += 1

                    if touchCounter[hand][finger] >= debounceFrames:
                        touch[hand][finger] = False
                        touchCounter[hand][finger] = 0
                        print("NOTE OFF: ", note_name)
                        stop_note(note_name)

                else:
                    touchCounter[hand][finger] = 0

def start_note(note):
    if note not in envelope:
        phase[note] = 0

        envelope[note] = {
            "state": "attack",
            "position": 0,
            "level": 0,
            "release_start": 0
        }
        keyHeld.append(note)

def stop_note(note):
    if note in keyHeld:
        keyHeld.remove(note)
    if note in envelope:
        env = envelope[note]

        env["release_start"] = env["level"]
        env["state"] = "release"
        env["position"] = 0

def update_hand_pressure(result):
    global targetPressure

    hands = result.hand_landmarks

    if len(hands) == 0:
        targetPressure = 0.0
        return

    palm_heights = []

    for hand in hands:
        wrist = hand[0]
        palm_heights.append(wrist.y)

    avg_y = sum(palm_heights) / len(palm_heights)

    # print(
    #     f"Y: {avg_y:.2f} | "
    #     f"Target: {targetPressure:.2f} | "
    #     f"Pressure: {bellowsPressure:.2f}"
    # )

    targetPressure = np.interp(
        avg_y,
        [0.20, 0.90],
        [1.0, 0.0]
    )


# Audio Functions
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

    # dt = frames / sample_rate

    bellowsPressure += (
        targetPressure - bellowsPressure
    ) * pressureSmoothing

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


while vid.isOpened():
    success, frame = vid.read()

    if not success:
        print("Ignoring empty Camera Frames")
        continue

    frame = cv.flip(cv.cvtColor(frame, cv.COLOR_BGR2RGB), 1)

    mpImage = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )


    detectorResult = detector.detect(mpImage)
    update_hand_pressure(detectorResult)

    define_points(detectorResult)
    distances = distance_Calc()
    # print(distances)
    update_touch(distances)
    result = draw_landmarks_on_image(frame, detectorResult)
    cv.imshow('Window', cv.cvtColor(result, cv.COLOR_RGB2BGR))

    if cv.waitKey(1) & 0xFF == ord('d'):
        break




stream.stop()
stream.close()

vid.release()
cv.destroyAllWindows()