import cv2
from typing import Optional
from . import get_camera, mongo
from flask_login import UserMixin
from dataclasses import dataclass
from heart_rate_monitor.tracker import Detector


@dataclass
class User(UserMixin):
    email: str
    full_name: str
    password: str
    hrt: Optional[Detector]
    camera: Optional[cv2.VideoCapture]
    video: bool = False

    def get_id(self):
        return self.email

    def video_on(self):
        self.video = True
        self.camera = get_camera()
        self.hrt = Detector(self.camera)

    def video_off(self):
        self.video = False
        self.camera.release()
        self.camera = None
        self.hrt = None
        


def get_user(email):
    users_collection = mongo.db.users
    user_data = users_collection.find_one({"_id": email})

    if user_data:
        camera = get_camera()
        hrt = Detector(camera)
        return User(
            email=user_data["_id"],
            full_name=user_data["full_name"],
            password=user_data["password"],
            camera=camera,
            hrt=hrt
        )


def save_user(email, full_name, password):
    users_collection = mongo.db.users
    users_collection.insert_one(
        {
            "_id": email,
            "full_name": full_name,
            "password": password,
        }
    )
