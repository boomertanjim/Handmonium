import cv2 as cv

vid = cv.VideoCapture('vid.mp4')

while True:
    isTrue, frame = vid.read()

    cv.imshow('Video', frame)

    if cv.waitKey(20) & 0xFF==ord('d'):
        break

vid.release()
cv.destroyAllWindows()