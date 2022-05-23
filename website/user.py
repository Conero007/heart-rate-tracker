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

    def get_id(self):
        return self.email


def get_user(email):
    users_collection = mongo.db.users
    user_data = users_collection.find_one({"_id": email})

    if user_data:
        webcam = get_camera()
        hrt = Detector(webcam)
        return User(
            email=user_data["_id"],
            full_name=user_data["full_name"],
            password=user_data["password"],
            camera=webcam,
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
