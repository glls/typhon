import cv2


class WindowManager(object):
    def __init__(self, window_name, keypress_callback=None, mouse_callback=None):
        self.keypress_callback = keypress_callback
        self.mouse_callback = mouse_callback

        self._window_name = window_name
        self._is_window_created = False
        self._wait_ms = 500

    @property
    def is_window_created(self):
        return self._is_window_created

    def set_delay(self, value):
        if self._wait_ms != value:
            self._wait_ms = value

    def create_window(self):
        cv2.namedWindow(self._window_name)
        if self.mouse_callback is not None:
            cv2.setMouseCallback(self._window_name, self.mouse_callback)
        self._is_window_created = True

    def show(self, frame):
        cv2.imshow(self._window_name, frame)

    def destroy_window(self):
        cv2.destroyWindow(self._window_name)
        self._is_window_created = False

    def process_events(self, paused):
        if paused:
            key_code = cv2.waitKey(0)
        else:
            key_code = cv2.waitKey(self._wait_ms)

        if self.keypress_callback is not None and key_code != -1:
            # Discard any non-ASCII info encoded by GTK
            key_code &= 0xFF
            self.keypress_callback(key_code)

        if self.mouse_callback is not None:
            self.mouse_callback
