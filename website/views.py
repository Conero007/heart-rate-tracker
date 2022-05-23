from flask_login import current_user, login_required
from flask import Blueprint, Response, redirect, render_template, url_for

views = Blueprint("views", __name__)


@views.route("/video_on", methods=["POST"])
@login_required
def video_on():
    current_user.video = True
    return redirect(url_for("views.home"))


@views.route("/video_off", methods=["POST"])
@login_required
def video_off():
    current_user.video = False
    return redirect(url_for("views.home"))


@views.route("/video_feed")
@login_required
def video_feed():
    return Response(
        current_user.hrt.gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@views.get("/")
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
