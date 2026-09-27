import cv2 as cv

def rescaleFrame (frame, scale=0.75):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    dimensions = (width, height)

    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)


capture = cv.VideoCapture("vid.mp4")

while True:
    isTrue, frame = capture.read()

    frameResized = rescaleFrame(frame, 0.2)

    # cv.imshow('video', frame)
    cv.imshow('Video Resized', frameResized)

    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()