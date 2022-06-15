import datetime
from threading import Lock, Thread
from time import sleep, time

import cv2 as cv
import numpy as np
import pyautogui as py


class State:
    LOGIN = 0
    SERVER = 1
    CHARACTER = 2
    IN_GAME = 3
    LOADING = 4
    RESET = 5


class ObjectDetection:
    image_flag_method = None
    match_template_method = None
    character_bar = None
    login = None
    server = None
    character = None
    loading = None
    back = None

    LOGIN_SECONDS = 10
    SERVER_SECONDS = 10
    CHARACTER_SECONDS = 5

    stopped = True
    lock = None
    screenshot = None
    current_state = None
    timestamp = None
    dc_times = 0
    attempt = 0

    scheduler = None

    def __init__(self):
        self.current_state = State.IN_GAME
        self.lock = Lock()
        self.timestamp = time()

        self.image_flag_method = cv.IMREAD_UNCHANGED
        self.match_template_method = cv.TM_CCOEFF_NORMED

        self.character_bar = cv.imread('in_game.jpg', self.image_flag_method)
        self.login = cv.imread('login.jpg', self.image_flag_method)
        self.server = cv.imread('server.jpg', self.image_flag_method)
        self.character = cv.imread('character.jpg', self.image_flag_method)
        self.loading = cv.imread('loading.jpg', self.image_flag_method)


    def detect_object(self, detected_object, threshold=0.5):
        result = cv.matchTemplate(self.screenshot, detected_object, self.match_template_method)
        locations = np.where(result >= threshold)

        return list(zip(*locations[::-1]))

    def is_disconnected(self):
        locations_login = self.detect_object(self.login)

        if locations_login:
            return True
        else:
            return False

    def update_state(self, state):
        self.current_state = state

    # Threading methods.

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def increase_attempt(self):
        self.attempt += 1
        # print('Current attempt:', self.attempt)

        if self.attempt > 1:
            print('The game is lagging heavily. Resetting the process...')

            self.current_state = State.RESET

    def run(self):
        while not self.stopped:
            if self.current_state == State.RESET:
                sleep(2)

                py.moveTo(77, 90)

                is_login_screen = self.is_disconnected()
                self.lock.acquire()

                if is_login_screen:
                    self.current_state = State.LOGIN
                    self.attempt = 0
                else:
                    py.click(interval=2)

                self.lock.release()
            elif self.current_state == State.LOGIN:
                # if time() > self.timestamp + 5:
                self.dc_times += 1

                py.moveTo(960, 744)

                locations_server = self.detect_object(self.server)
                self.lock.acquire()

                if not locations_server:
                    py.click(interval=2)
                else:
                    self.current_state = State.SERVER

                self.lock.release()
            elif self.current_state == State.SERVER:
                sleep(2)

                print('Server selection...')

                py.moveTo(975, 359)

                locations_character = self.detect_object(self.character)
                self.lock.acquire()

                if not locations_character:
                    py.click(interval=1, clicks=2)
                    self.increase_attempt()
                else:
                    self.current_state = State.CHARACTER
                    self.attempt = 0
                    py.moveTo(790, 1016)
                self.lock.release()
            elif self.current_state == State.CHARACTER:
                sleep(5)

                # print('Character selection...')

                locations_loading = self.detect_object(self.loading)
                self.lock.acquire()

                if not locations_loading:
                    # py.click(interval=5)
                    self.increase_attempt()
                else:
                    self.current_state = State.LOADING
                    self.attempt = 0

                self.lock.release()
            elif self.current_state == State.LOADING:
                # print('Waiting for 10 seconds to load the game.')

                sleep(10)

                self.lock.acquire()
                self.current_state = State.IN_GAME
                self.lock.release()

                print('Back to fishing at {}.'.format(datetime.datetime.now()))
