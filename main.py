import datetime

import cv2 as cv

from object_detection import ObjectDetection
from windowcapture import WindowCapture

window = WindowCapture(None)
bot = ObjectDetection()

window.start()
bot.start()


class State:
    LOGIN = 0
    SERVER = 1
    CHARACTER = 2
    IN_GAME = 3
    LOADING = 4
    RESET = 5


while True:
    if window.screenshot is None:
        continue

    if bot.current_state == State.IN_GAME:
        bot.update(window.screenshot)
        disconnected = bot.is_disconnected()

        if disconnected:
            print('Disconnected at {}.'.format(datetime.datetime.now()))

            bot.update_state(State.LOGIN)
    elif bot.current_state == State.LOGIN:
        bot.update(window.screenshot)
    elif bot.current_state == State.SERVER:
        bot.update(window.screenshot)
    elif bot.current_state == State.CHARACTER:
        bot.update(window.screenshot)
    elif bot.current_state == State.RESET:
        bot.update(window.screenshot)

    key = cv.waitKey(1) & 0xFF  # Waits 1ms every loop to process key presses.

    if key == ord('z'):
        window.stop()
        bot.stop()
        cv.destroyAllWindows()
        break

print('Peacefully closing the app.')
