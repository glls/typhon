from __future__ import print_function
from __future__ import unicode_literals

try:
    import Image
except ImportError:
    from PIL import Image

import cv2
import sys
import os.path
import numpy as np
import pytesseract

from capturemanager import CaptureManager
from windowmanager import WindowManager


class TyphonApp(object):
    def __init__(self):
        """
        initialization
        """
        if len(sys.argv) <= 1:
            print("Usage: typhon.py filename")
            exit(255)
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print("File '" + filename + "' not found")
            exit(254)
        self._windowManager = WindowManager('Typhon', self.on_keypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(filename), self._windowManager)
        self.current_frame = None
        self._draw_info = True
        self._draw_help = False
        self.paused = True
        self._ocr = False

    def run(self):
        self._windowManager.create_window()

        """
        Main loop
        """
        while self._windowManager.is_window_created:
            self._captureManager.enter_frame()
            frame = self._captureManager.frame
            # BEGIN
            self.current_frame = self._captureManager.frames_elapsed
            #########################################################

            # frame = self.rotate_image(frame, 45)
            if self._ocr:
                self.image_to_text(frame)
                self._ocr = False

            if self._draw_info:
                txt = "Frame: " + str(self.current_frame) + "/" + \
                      str(self._captureManager.total_frames)
                self.draw_text(frame, txt, (10, 60), (255,) * 3)
                if not self._draw_help:
                    self.draw_text(frame, 'Press [h] for help', (10, 100), (255,) * 3)

            if self._draw_help:
                self.draw_help(frame)

            # END
            self._captureManager.exit_frame()
            self._windowManager.process_events(self.paused)

    # def mouse_event(self, event, x, y, flags, param):
    #     print ("Mouse event :", event, x, y, flags, param)
    #     return

    def on_keypress(self, keycode):
        # print('Keycode #', keycode)
        if keycode == 27:  # ESC, quit
            self._windowManager.destroy_window()
        elif keycode == ord('p'):
            self.paused = not self.paused
        elif keycode == ord('h'):
            self._draw_help = not self._draw_help
        elif keycode == ord('t'):
            self._ocr = True
        elif keycode == ord('s'):
            self._captureManager.write_image('screenshot.png')
        elif keycode == ord('i'):
            self._draw_info = not self._draw_info
        elif keycode == ord('b'):  # go back 50 frames
            self._captureManager.frames_elapsed -= 51
        elif keycode == ord('n'):  # forward 50 frames
            self._captureManager.frames_elapsed += 49
        elif keycode == 81:  # go back 5 frames
            self._captureManager.frames_elapsed -= 6
        elif keycode == 83:  # forward 5 frames
            self._captureManager.frames_elapsed += 4
        elif 48 <= keycode <= 57:
            print(self._captureManager.fps)
            a = ((keycode - 48) * 100)
            print('Delay:', a)
            if a == 0:
                a = 1
            self._windowManager.set_delay(int(a))

    def draw_help(self, frame):
        sy = 200
        color = (0, 255, 128)  # lime
        txt = "====== Help ======"
        self.draw_text(frame, txt, (10, sy), color)
        txt = "[ESC] Quit"
        self.draw_text(frame, txt, (10, sy + 25), color)
        txt = "[p] Pause mode " + ("ON" if self.paused else "OFF")
        self.draw_text(frame, txt, (10, sy + 50), color)
        txt = "[t] OCR and print result"
        self.draw_text(frame, txt, (10, sy + 75), color)
        txt = "[b]/[n] REW/FFD 50 frames"
        self.draw_text(frame, txt, (10, sy + 100), color)
        txt = "[LEFT]/[RIGHT] REW/FFD 5 frames"
        self.draw_text(frame, txt, (10, sy + 125), color)
        txt = "[s] Save screenshot"
        self.draw_text(frame, txt, (10, sy + 150), color)
        txt = "[0]-[9] Set delay"
        self.draw_text(frame, txt, (10, sy + 175), color)

    def outline_rect(self, image, rect, color, thickness=1):
        # color is in BGR
        # e.g. outlineRect(frame, (10, 10, 400, 200), (255, 128, 0))
        if rect is None:
            return
        x, y, w, h = rect
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)

    def rotate_image(self, image, angle):
        center = tuple(np.array(image.shape[0:2]) / 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rot_mat, image.shape[0:2], flags=cv2.INTER_LINEAR)

    def draw_text(self, frame, text, pos, color):
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, .5, (0,) * 3, 2, cv2.CV_AA)
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1, cv2.CV_AA)

    def image_to_text(self, img):
        a = np.asarray(img)
        i = Image.fromarray(a)
        print(pytesseract.image_to_string(i))


if __name__ == "__main__":
    print("Typhon v1.1 - Interactive video to text converter\n")
    # print("Python version", sys.version)
    # print("OpenCV version", cv2.__version__)
    TyphonApp().run()
