import cv2 as cv
import mediapipe as mp
mpDrawing = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles
mpHands = mp.solutions.hands

vid = cv.VideoCapture(0);

if not vid.isOpened():
    print("ERROR")
    exit()

with mpHands.Hands(
    model_complexity = 0,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:
    while vid.isOpened():
        success, frame = vid.read()

        if not success:
            print("Ignoring empty Camera Frames")
            continue

        frame.flags.writable = False
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(frame)

        frame.flags.writable = True
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        if results.multiHandLandmarks:
            for handLandmarks in results.multiHandLandmarks:
                mpDrawing.draw_landmarks(
                    frame,
                    handLandmarks,
                    mpHands.HAND_CONNECTIONS,
                    mpDrawingStyles.get_default_hand_landmarks_style(),
                    mpDrawingStyles.get_default_hand_connections_style()
                )

        cv.imshow('WebCam Test', cv.flip(frame, 1))

        if cv.waitKey(1) & 0xFF == ord('d'):
            break


vid.release()
cv.destroyAllWindows()