import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

baseOptions = python.BaseOptions(model_asset_path = "hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options = baseOptions,
                                       num_hands = 2)
detector = vision.HandLandmarker.create_from_options(options)

image = mp.Image.create_from_file("image.jpg")

detectorResult = detector.detect(image)

for handLandmarks in detectorResult.hand_landmarks[0]:
    print ("X--> " + str(handLandmarks.x) + "Y-->" + str(handLandmarks.y))

# result = draw_landmarks_on_image(image.numpy_view(), detectorResult)
# cv.imshow(cv.cvtColor(result, cv.COLOR_RGB2BGR))




# vid = cv.VideoCapture(0);

# if not vid.isOpened():
#     print("ERROR")
#     exit()

# with mpHands.Hands(
#     model_complexity = 0,
#     min_detection_confidence = 0.5,
#     min_tracking_confidence = 0.5) as hands:
#     while vid.isOpened():
#         success, frame = vid.read()

#         if not success:
#             print("Ignoring empty Camera Frames")
#             continue

#         frame.flags.writable = False
#         frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#         results = hands.process(frame)

#         frame.flags.writable = True
#         frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#         if results.multiHandLandmarks:
#             for handLandmarks in results.multiHandLandmarks:
#                 mpDrawing.draw_landmarks(
#                     frame,
#                     handLandmarks,
#                     mpHands.HAND_CONNECTIONS,
#                     mpDrawingStyles.get_default_hand_landmarks_style(),
#                     mpDrawingStyles.get_default_hand_connections_style()
#                 )

#         cv.imshow('WebCam Test', cv.flip(frame, 1))

#         if cv.waitKey(1) & 0xFF == ord('d'):
#             break


# vid.release()
# cv.destroyAllWindows()