import cv2
from typing import Optional

class CameraService:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception("Kamera başlatılamadı!")

    def read_frame(self):
        if self.cap is None:
            raise Exception("Kamera başlatılmadı!")
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Frame okunamadı!")
        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None 