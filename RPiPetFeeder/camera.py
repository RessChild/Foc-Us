import time
import io
import threading
import picamera
from PIL import Image


class Camera(object):
    thread = None
    frame = None
    last_access = 0

    def initialize(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    def _thread(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True

            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                im = Image.open(stream)
                im.save('./static/img.jpg', 'JPEG')
                stream.seek(0)
                self.frame = stream.read()

                stream.seek(0)
                stream.truncate()

                if time.time() - Camera.last_access > 10:
                    break
        thread = None