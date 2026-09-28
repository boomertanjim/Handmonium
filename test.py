import cv2 as cv
import numpy as np

blank = np.zeros((500, 500, 3), dtype='uint8')

cv.rectangle(blank, (0,0), (250,250), (0,255,0), thickness=cv.FILLED )

cv.circle(blank, (blank.shape[0]//2, blank.shape[1]//2), 40, (255, 0, 243), thickness=2, )

cv.line(blank, (0,0), (blank.shape[0]//2, blank.shape[1]//2), (233, 0, 233), thickness=4)

cv.imshow('green', blank)
cv.waitKey(0)

# def rescaleFrame (frame, scale=0.75):
#     width = int(frame.shape[1] * scale)
#     height = int(frame.shape[0] * scale)

#     dimensions = (width, height)

#     return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)




# capture = cv.VideoCapture("vid.mp4")

# while True:
#     isTrue, frame = capture.read()

#     frameResized = rescaleFrame(frame, 0.2)

#     # cv.imshow('video', frame)
#     cv.imshow('Video Resized', frameResized)

#     if cv.waitKey(20) & 0xFF == ord('d'):
#         break

# capture.release()
# cv.destroyAllWindows()