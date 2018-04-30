import cv2
import time
import math


class CaptureManager(object):
    def __init__(self, capture, preview_window_manager=None):

        self.preview_window_manager = preview_window_manager

        # VideoCapture, e.g.  0=1st camera or a filename
        self._capture = capture
        self._channel = 0
        self._entered_frame = False
        self._frame = None
        self._image_filename = None
        self._start_time = None
        self._frames_elapsed = int(0)
        self._fps_estimate = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._entered_frame and self._frame is None:
            _, self._frame = self._capture.retrieve()
        return self._frame

    @property
    def frames_elapsed(self):
        return self._frames_elapsed

    @frames_elapsed.setter
    def frames_elapsed(self, value):
        if value < 0:
            value = 0
        self.goto_frame(value)
        self._frames_elapsed = value

    @property
    def fps(self):
        fps = self._capture.get(cv2.cv.CV_CAP_PROP_FPS)
        if math.isnan(fps):
            fps = self._fps_estimate
        return fps

    @property
    def total_frames(self):
        return int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

    @property
    def video_size(self):
        return (int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
                int(self._capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))

    @property
    def is_writing_image(self):
        return self._image_filename is not None

    def enter_frame(self):
        """
        Capture the next frame, if any
        But first, check that any previous frame was exited.
        """
        assert not self._entered_frame, \
            'previous enter_frame() had no matching exit_frame()'

        if self._capture is not None:
            self._entered_frame = self._capture.grab()

    def exit_frame(self):
        """
        Draw to the window. Write to files. Release the frame
        Check whether any grabbed frame is retrievable
        The getter may retrieve and cache the frame
        """
        if self.frame is None:
            self._entered_frame = False
            return

        # Update the FPS estimate and related variables
        if self._frames_elapsed == 0:
            self._start_time = time.time()
        else:
            time_elapsed = time.time() - self._start_time
            self._fps_estimate = self._frames_elapsed / time_elapsed
        self._frames_elapsed += 1

        # Draw to the window, if any.
        if self.preview_window_manager is not None:
            self.preview_window_manager.show(self._frame)

        # Write to the image file, if any
        if self.is_writing_image:
            cv2.imwrite(self._image_filename, self._frame)
            self._image_filename = None

        # Release the frame.
        self._frame = None
        self._entered_frame = False

    def write_image(self, filename):
        """
        Write the next exited frame to an image file
        """
        self._image_filename = filename

    def goto_frame(self, frame_number):
        self._capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_number)
        if self._capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == frame_number:
            return True
