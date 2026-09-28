import cv2 as cv
import numpy as np

vid = cv.VideoCapture(0);

if not vid.isOpened():
    print("ERROR")
    exit()

while True:
    ret, frame = vid.read()

    flipped = cv.flip(frame, 1)

    cv.imshow('WebCam Test', flipped)

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

vid.release()
cv.destroyAllWindows()