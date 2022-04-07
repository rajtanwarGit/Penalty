import cv2
import numpy as np
from PIL import Image
import mss
from ppadb.client import Client
import threading
import time

shoot_x = 0
shoot_y = 0

input('press enter to start..')

adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

def calcX():
    x_percent = (shoot_x * 100) / 410
    return (x_percent * 1080) / 100

def calcY():
    y_percent = (shoot_y * 100) / 450
    return (y_percent * 2273) / 100


running = True
def shoot():
    GO = False
    tempX, tempY = 1.0, 1.0

    while running:
        scrn_x = calcX()
        scrn_y = calcY()

        if(scrn_x != tempX and scrn_y != tempY):
            GO = True

        if(GO):
            device.shell(f'input touchscreen swipe 540 1920 {scrn_x} {scrn_y} 100')
            time.sleep(0.8)
            print(scrn_x, scrn_y)
            GO = False

        tempX, tempY = scrn_x, scrn_y

t1 = threading.Thread(target=shoot)
t1.start()

t2 = threading.Thread(target=calcX)
t2.start()

t3 = threading.Thread(target=calcY)
t3.start()

sct = mss.mss()

while True:
    scr = sct.grab({
        'left': 15,
        'top':  200,
        'width': 410,
        'height': 250
    })

    img = np.array(scr)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT,
        1, 20,
        param1=70, param2=70,
        minRadius=10, maxRadius=20)

    if circles is not None:
        circles = np.uint16(circles)

        for pt in circles[0, :]:
            x, y, r = pt[0], pt[1], pt[2]
            cv2.circle(img, (x, y), r, (0, 255, 200), 5)
            shoot_x = x
            shoot_y = y

    cv2.imshow('output', img)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        running = False
        break
