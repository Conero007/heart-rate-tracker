import cv2
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from .constants import init_constants


mongo = PyMongo()


def create_app():
    app = Flask(__name__)

    app.config["MONGO_URI"] = init_constants["MONGO_URI"]
    app.config["SECRET_KEY"] = init_constants["APP_CONFIG_SECRET_KEY"]

    mongo.init_app(app)

    from .auth import auth
    from .views import views

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .user import get_user

    @login_manager.user_loader
    def load_user(email):
        return get_user(email)

    return app


def get_camera():
    for i in range(8):
        cam = cv2.VideoCapture(i)
        if cam and cam.isOpened():
            return cam
    raise ValueError("Camera Not Found")
