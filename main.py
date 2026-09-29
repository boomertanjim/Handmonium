import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

baseOptions = python.BaseOptions(model_asset_path = "hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options = baseOptions,
                                       num_hands = 2)
detector = vision.HandLandmarker.create_from_options(options)

vid = cv.VideoCapture(0)

# vid.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
# vid.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
# vid.set(cv.CAP_PROP_FPS, 30)

cords = [
    [
        (),
        (),
        (),
        (),
        ()
    ],
    [
        (),
        (),
        (),
        (),
        ()
    ]
]

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
        [(), (), (), (), ()],
        [(), (), (), (), ()]
    ]

    hands = result.hand_landmarks

    for handIndex, hand in enumerate(hands):
        for i in range(4, 21, 4):
            cords[handIndex][i // 4 - 1] = (hand[i].x, hand[i].y)

def find_distance (a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def distance_Calc():
    ans = []

    for i in range(2):
        hand = []

        for j in range (1, 5):
            if cords[i][0] and cords [i][j]:
                hand.append(find_distance(cords[i][0], cords[i][j]))
            else:
                hand.append(0)

        ans.append(hand)

    return ans

def write_Distance(frame, distances):
    names = ["index", "middle", "ring", "pinky"]

    for i in range(2):
        for j in range(4):
            if i == 0:
                y = j * 30 + 30
            else:
                y = j * 30 + 150

            if distances[i][j] == 0:
                isTouching = "No Hands"
            elif distances[i][j] < 0.044:
                isTouching = "Touching"
            else:
                isTouching = "Not Touching"
            cv.putText(
                frame,
                f"{names[j]} {i}: {isTouching}",
                (10, y),
                cv.FONT_HERSHEY_COMPLEX,
                0.7,
                (0, 0, 255),
                2
                )

    

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



    define_points(detectorResult)
    distances = distance_Calc()
    write_Distance(frame, distances)
    result = draw_landmarks_on_image(frame, detectorResult)
    cv.imshow('Window',cv.cvtColor(result, cv.COLOR_RGB2BGR))

    if cv.waitKey(1) & 0xFF == ord('d'):
        break



vid.release()
cv.destroyAllWindows()