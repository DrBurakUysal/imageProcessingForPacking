import cv2
import numpy as np
from typing import List
from .detector import ObjectDetector
from ..models.product import Product

class YOLODetector(ObjectDetector):
    def __init__(self, weights_path: str, config_path: str, classes_path: str):
        try:
            self.net = cv2.dnn.readNet(weights_path, config_path)
        except cv2.error as e:
            print(f"Hata: YOLOv3 dosyaları yüklenirken hata oluştu!")
            print(f"weights_path: {weights_path}")
            print(f"config_path: {config_path}")
            print(f"Hata mesajı: {str(e)}")
            raise

        try:
            with open(classes_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Hata: classes dosyası okunamadı: {classes_path}")
            print(f"Hata mesajı: {str(e)}")
            raise

        try:
            self.layer_names = self.net.getLayerNames()
            output_layers = self.net.getUnconnectedOutLayers()
            self.output_layers = [self.layer_names[i - 1] for i in output_layers.flatten()]
        except Exception as e:
            print("Hata: YOLO katmanları alınırken hata oluştu!")
            print(f"Hata mesajı: {str(e)}")
            raise

    def detect_box(self, frame) -> bool:
        try:
            products = self.detect_products(frame)
            return any(p.name in ["box", "suitcase", "backpack"] and p.confidence > 0.2 for p in products)
        except Exception as e:
            print(f"Hata: Koli tespiti sırasında hata oluştu: {str(e)}")
            return False

    def detect_products(self, frame) -> List[Product]:
        try:
            height, width, _ = frame.shape
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            class_ids = []
            confidences = []
            boxes = []

            # Tespit hassasiyetini düşür
            confidence_threshold = 0.2

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > confidence_threshold:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)
            products = []
            
            if len(indexes) > 0:
                for i in indexes.flatten():
                    # Debug bilgisi
                    print(f"Tespit: {self.classes[class_ids[i]]} ({confidences[i]:.2f})")
                    products.append(Product(
                        name=self.classes[class_ids[i]],
                        confidence=confidences[i],
                        bbox=boxes[i]  # x, y, w, h koordinatlarını da ekle
                    ))

            return products
        except Exception as e:
            print(f"Hata: Ürün tespiti sırasında hata oluştu: {str(e)}")
            return [] 