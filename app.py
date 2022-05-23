import cv2
from website import create_app
from heart_rate_monitor.monitor_new import Monitor

app = create_app()


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    print(Monitor(cv2.VideoCapture(0)))
