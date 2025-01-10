import json
import os
import cv2
from datetime import datetime
from typing import List
from ..models.box import Box

class StorageService:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.boxes_file = os.path.join(storage_dir, 'boxes.json')
        self.images_dir = os.path.join(storage_dir, 'images')
        
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def save_box(self, box: Box):
        boxes = self.get_boxes()
        boxes.append(box.to_dict())
        
        with open(self.boxes_file, 'w') as f:
            json.dump(boxes, f)

    def get_boxes(self) -> List[dict]:
        if not os.path.exists(self.boxes_file):
            return []
        
        with open(self.boxes_file, 'r') as f:
            return json.load(f)

    def save_image(self, image, box_id: str, products=None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"box_{box_id}_{timestamp}.jpg"
        path = os.path.join(self.images_dir, filename)
        
        # Eğer ürünler varsa, çerçeve çiz
        if products:
            image_copy = image.copy()
            for product in products:
                x, y, w, h = product.bbox
                # Çerçeve çiz
                cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # İsim ve güven değerini yaz
                text = f"{product.name} ({product.confidence:.2f})"
                cv2.putText(image_copy, 
                           text,
                           (x, y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5,
                           (0, 255, 0), 
                           2)
            cv2.imwrite(path, image_copy)
        else:
            cv2.imwrite(path, image)
        return path 

    def delete_box(self, box_id: str):
        boxes = self.get_boxes()
        
        # Silinecek koliyi bul
        box = next((b for b in boxes if b['id'] == box_id), None)
        if box:
            # Görsel dosyasını sil
            if os.path.exists(box['image_path']):
                os.remove(box['image_path'])
            
            # Koliyi listeden çıkar
            boxes = [b for b in boxes if b['id'] != box_id]
            
            # Güncellenmiş listeyi kaydet
            with open(self.boxes_file, 'w') as f:
                json.dump(boxes, f) 