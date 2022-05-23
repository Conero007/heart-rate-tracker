import cv2
from flask_login import current_user, login_required
from flask import Blueprint, Response, render_template

from website import get_camera

views = Blueprint("views", __name__)


@views.route("/video_feed")
def video_feed():
    return Response(current_user.hrt.gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@views.route("/")
@login_required
def home():
    return render_template("home.html", user=current_user)


# def gen_frames(camera):
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         frame = cv2.flip(frame, 1)
#         _, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()
#         yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
