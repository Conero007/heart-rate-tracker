import cv2
from flask import Flask


def get_camera():
    for i in range(8):
        cam = cv2.VideoCapture(i)
        if cam and cam.isOpened():
            return cam
    raise ValueError("Camera Not Found")


camera = get_camera()


def create_app():
    app = Flask(__name__)

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
