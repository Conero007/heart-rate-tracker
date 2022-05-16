from website import gen_frames
from flask import Blueprint, Response, render_template

views = Blueprint("views", __name__)


@views.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@views.route("/")
def index():
    return render_template("home.html")
