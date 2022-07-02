import datetime
from time import sleep

import cv2 as cv
import win32api
import win32con
import win32gui

from object_detection import ObjectDetection
from windowcapture import WindowCapture

window = WindowCapture(None)
bot = ObjectDetection()

window.start()
bot.start()

window_name = "Rise Online Client"
hwnd = win32gui.FindWindow(None, window_name)


class State:
    LOGIN = 0
    SERVER = 1
    CHARACTER = 2
    IN_GAME = 3
    LOADING = 4
    RESET = 5


fishing_started = False

while True:
    if window.screenshot is None:
        continue

    # http://kbdedit.com/manual/low_level_vk_list.html

    if bot.current_state == State.IN_GAME:
        bot.update(window.screenshot)

        if not fishing_started:
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x59, 0)
            sleep(0.5)
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x59, 0)

            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x46, 0)
            sleep(0.5)
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x46, 0)

            fishing_started = True

        disconnected = bot.is_disconnected()

        if disconnected:
            fishing_started = False
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
