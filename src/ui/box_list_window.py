from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QListWidget, QLabel, QPushButton)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2

class BoxListWindow(QMainWindow):
    def __init__(self, storage_service):
        super().__init__()
        self.storage_service = storage_service
        self.setup_ui()
        self.load_boxes()

    def setup_ui(self):
        self.setWindowTitle("Koli Listesi")
        self.setGeometry(150, 150, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Sol taraf - Koli listesi
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.box_list = QListWidget()
        self.box_list.setMinimumWidth(300)
        self.box_list.itemClicked.connect(self.show_box_details)
        left_layout.addWidget(self.box_list)
        
        layout.addWidget(left_widget, stretch=2)
        
        # Sağ taraf - Koli detayları
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 500)
        right_layout.addWidget(self.image_label)
        
        self.products_label = QLabel()
        self.products_label.setAlignment(Qt.AlignTop)
        right_layout.addWidget(self.products_label)
        
        layout.addWidget(right_widget, stretch=3)

    def load_boxes(self):
        boxes = self.storage_service.get_boxes()
        self.box_list.clear()
        
        for box in boxes:
            self.box_list.addItem(f"Koli: {box['id']} - {box['timestamp']}")

    def show_box_details(self, item):
        box_id = item.text().split(' - ')[0].split(': ')[1]
        boxes = self.storage_service.get_boxes()
        
        box = next((b for b in boxes if b['id'] == box_id), None)
        if box:
            # Görsel gösterimi
            image = cv2.imread(box['image_path'])
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                
                # Görüntüyü pencereye sığdır
                max_height = 400
                if height > max_height:
                    ratio = max_height / height
                    new_width = int(width * ratio)
                    image = cv2.resize(image, (new_width, max_height))
                    height, width, channel = image.shape

                bytes_per_line = 3 * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_image))
            
            # Ürün listesi gösterimi
            products_text = "Tespit Edilen Ürünler:\n\n"
            for product in box['products']:
                confidence = float(product['confidence']) * 100
                products_text += f"• {product['name']} (Güven: %{confidence:.1f})\n"
            
            self.products_label.setText(products_text) 