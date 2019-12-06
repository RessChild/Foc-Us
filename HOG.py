from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import cv2
import time

cap = cv2.VideoCapture(0)

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# initialize the camera and grab a reference to the raw camera capture
vs = VideoStream(usePiCamera=True).start()

# allow the camera to warmup
time.sleep(2.0)

# capture frames from the camera
while True:
# grab the raw NumPy array representing the image, then initialize the timestamp
# and occupied/unoccupied text
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
 	# (h, w) = frame.shape[:2]
	# image = frame.array
	# image = imutils.resize(image, width=min(400, image.shape[1]))
	# detect people in the image
    (rects, weights) = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
    if len(rects) > 0:
        for (x, y , w, h) in rects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
# draw the original bounding boxes
# apply non-maxima suppression to the bounding boxes using a
# fairly large overlap threshold to try to maintain overlapping
# boxes that are still people
    
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        # pick = non_max_suppression(frame, probs=None, overlapThresh=0.65)
        non_max_suppression(frame, probs=None, overlapThresh=0.65)
        (x1, y1, w1, h1) = rects.astype("int")[0]

    # draw the final bounding boxes
        cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0),2)    
    # show the frame
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF

# clear the stream in preparation for the next frame
# rawCapture.truncate(0)

# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

cv2.destroyAllWindow()
vs.stop()

