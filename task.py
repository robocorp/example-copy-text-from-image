import numpy
import cv2
import pytesseract
import mss
import pyperclip

# TAKE A SCREENSHOT
# in multi-monitor environments you may want to change this monitor number
MONITOR = 0

with mss.mss() as sct:
    monitor = sct.monitors[MONITOR]
    bgra = numpy.array(sct.grab(monitor))

# remove the alpha channel
bgr = cv2.cvtColor(bgra, cv2.COLOR_BGRA2BGR)

# PREPARE MOUSE EVENT HANDLER
# top-left and bottom-right points (x, y) of selected region
px = py = []
cropping = False


def click_and_crop(event, x, y, flags, param):
    global px, py, cropping

    if event == cv2.EVENT_LBUTTONDOWN:
        px = [x, x]
        py = [y, y]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        px[1] = x
        py[1] = y
        cropping = False
    elif event == cv2.EVENT_MOUSEMOVE and cropping:
        px[1] = x
        py[1] = y


# SELECT REGION IN SEPARATE WINDOW
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

# original screenshot is stored in bgr and we use a copy to show the selection
image = bgr.copy()
cv2.imshow('image', image)
cv2.waitKey(1)

cx = cy = []

while cropping or not px:
    if cropping and (set(cx) != set(px) or set(cy) != set(py)):
        # clear the selection by copying the region from original image
        if cx:
            image[cy[0]:cy[1]+1, cx[0]:cx[1]+1] = bgr[cy[0]:cy[1]+1, cx[0]:cx[1]+1]
        # update corners and draw selection
        cx = sorted(px)
        cy = sorted(py)

        cv2.rectangle(image, (cx[0], cy[0]), (cx[1], cy[1]), (0, 255, 0), 1)
        cv2.imshow('image', image)

    cv2.waitKey(1)

cv2.destroyWindow("image")
cv2.waitKey(1)
cv2.waitKey(1)  # workaround for opencv(?) bug
cv2.waitKey(1)  # workaround for opencv(?) bug
cv2.waitKey(1)  # workaround for opencv(?) bug

# OCR THE SELECTION AND SEND IT TO CLIPBOARD
roi = bgr[cy[0]:cy[1], cx[0]:cx[1]]
text = pytesseract.image_to_string(roi)
pyperclip.copy(text)
