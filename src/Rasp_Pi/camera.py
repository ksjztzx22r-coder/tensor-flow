import cv2

from Rasp_Pi.raspi_config import *

# ==========================================================
# Camera Class
# ==========================================================

class Camera:

    def __init__(self):

        self.cap = cv2.VideoCapture(0)

        self.cap.set(

            cv2.CAP_PROP_FRAME_WIDTH,

            CAMERA_WIDTH

        )

        self.cap.set(

            cv2.CAP_PROP_FRAME_HEIGHT,

            CAMERA_HEIGHT

        )

        self.cap.set(

            cv2.CAP_PROP_FPS,

            CAMERA_FPS

        )

        if not self.cap.isOpened():

            raise RuntimeError(

                "Unable to open camera."

            )

    def read(self):

        ret, frame = self.cap.read()

        if not ret:

            return None

        return frame

    def release(self):

        self.cap.release()


camera = None

def initialize_camera():

    global camera

    if camera is None:

        camera = Camera()


def get_frame():

    initialize_camera()

    return camera.read()


def close_camera():

    global camera

    if camera is not None:

        camera.release()

        camera = None


# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    while True:

        frame = get_frame()

        if frame is None:

            continue

        cv2.imshow(

            "Live Camera",

            frame

        )

        key = cv2.waitKey(1)

        if key == ord("q"):

            break

    close_camera()

    cv2.destroyAllWindows()