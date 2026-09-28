import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

baseOptions = python.BaseOptions(model_asset_path = "hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options = baseOptions,
                                       num_hands = 2)
detector = vision.HandLandmarker.create_from_options(options)

vid = cv.VideoCapture(0)

if not vid.isOpened():
    print("ERROR")
    exit()

image = mp.Image.create_from_file("image.jpg")

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
            print(landmark.z)
            radius = int(14 * abs(landmark.z))

            cv.circle(
                frame,
                (xCord, yCord),
                radius,
                (0, 255, 0),
                10
            )


    return frame

while vid.isOpened():
    success, frame = vid.read()

    if not success:
        print("Ignoring empty Camera Frames")
        continue

    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    mpImage = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )

    detectorResult = detector.detect(mpImage)
    result = draw_landmarks_on_image(frame, detectorResult)
    cv.imshow('Window',cv.cvtColor(result, cv.COLOR_RGB2BGR))

    if cv.waitKey(1) & 0xFF == ord('d'):
        break



vid.release()
cv.destroyAllWindows()