# Handmonium
Handmonium is python-based gesture controlled digital harmonium that let's you play notes using your hands

## Description
Handmonium uses a webcam and hand tracking to detect finger movements and translate them to musical notes. Bringing a finger close to the thumb triggers a note, allowing the user play multiple notes at once.

The application simulates the bellows of a traditional Harmonium. Moving hands vertically controls the virtual bellow pressure and it affects the volume and character of the sound.

The sound is synthesized digitally rather than using recordings. Each note uses 20 sine waveform with additional reed-like processing to create the harmonium-like sound.

Handmonium uses MediaPipe for real-time hand tracking, OpenCV for video capture and video frame manipulation, SoundDevice for real-time audio generation and PySide6 for the desktop interface.

### Screenshots
<img width="1184" height="937" alt="image" src="https://github.com/user-attachments/assets/f646edca-b05e-47e6-a51b-1562a0d81b0f" />

## Features

- Real-time synthesis
- Real-time hand tracking
- Finger-based note playing
- Supports two hands simultaneously
- Automatic right/left hand detection
- Bellow Pressure control
- ADSR support
- Total eight note polyphony
- Eight playable Notes
- Camera Selection drop down
- Real-time fingertip visualizaton
- Clean desktop GUI

## Controls

Handmonium currently uses the following finger mapping:

| Hand  | Finger | Note |
| ----  | ------ | ---- |
| Right | Index  | C4   |
| Right | Middle | D4   |
| Right | Ring   | E4   |
| Right | Pinky  | F4   |
| Left  | Index  | G4   |
| Left  | Middle | A4   |
| Left  | Ring   | B4   |
| Left  | Pinky  | C5   |

To play a note, bring the corresponding finger close to the thumb.

Moving the hand vertically controls bellow pressure. Higher hand positions produce larger pressure.

## How It Works

```text
Webcam
  ↓
OpenCV
  ↓
MediaPipe Hand Tracking
  ↓
Finger Position Detection
  ↓
Finger Distance Calculation
  ↓
Note Detection
  ↓
Audio Synthesis
  ↓
Sound Output
```

## Built With

- Python
- OpenCV
- MediaPipe
- SoundDevice
- Numpy
- PySide6
- PyInstaller

## How to Install

Download the latest Windows Release from the [Releases][]

After Downloading:
1. Extract the .ZIP file.
2. Open extracted folder.
3. Run `Handmonium.exe`.
4. Allow the application to access your camera if Windows asks for permission

## Running From Source
If you want to run the application from source, install the required Python packages:

```Bash
pip install opencv-python mediapipe numpy sounddevice PySide6
```

Then make sure `hand_landmark.task` is located in the same directory as `main.py`.

Run:

```bash
python main.py
```

## Building From Source
The application can be packaged using PyInstaller

For a standalone Windows application:

```bash
pyinstaller --onedir --windowed --collect-all mediapipe --add-data "hand_landmarker.task;." main.py
```

The packaged application will be generated inside the `dist` directory

## Help
### 1. The camera isn't detected 

Make Sure:
* Your Webcam is connected.
* Windows has granted camera permission to the application.
* Another application isn't using the webcam.

### 2. Hand tracking isn't working properly

Try using better lighting and keeping your hands clearly visible.

MediaPipe may have difficulties detecting hands when:

* The Environment is too dark or too bright.
* Yours hands are heavily obstructed.
* The camera image is blurry.

### 3. The notes trigger incorrectly

Keep your hand reasonably close to the camera.

### 4. The application isn't starting

Handmonium initializes MediaPipe's hand-tracking model and camera when starting, this significantly increases opening time.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
