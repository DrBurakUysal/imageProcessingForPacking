from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QInputDialog, QHBoxLayout,
                           QMessageBox, QTabWidget, QListWidget, QTableWidget,
                           QTableWidgetItem, QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from ..models.box import Box
from ..models.request import BoxRequest, Request
from random import randint, choice
import os
from datetime import datetime

class ComparisonDialog(QDialog):
    def __init__(self, comparison_result, parent=None):
        super().__init__(parent)
        self.setup_ui(comparison_result)

    def setup_ui(self, result):
        self.setWindowTitle("Koli Karşılaştırma")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(self)

        # Sonuç başlığı
        status = "UYUMLU ✅" if result['matching'] else "UYUMSUZ ❌"
        title = QLabel(f"Karşılaştırma Sonucu: {status}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        if not result['matching']:
            # Farklılıkları tablo halinde göster
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Ürün", "Beklenen", "Gerçek"])
            table.setRowCount(len(result['differences']))

            for i, diff in enumerate(result['differences']):
                table.setItem(i, 0, QTableWidgetItem(diff['product']))
                table.setItem(i, 1, QTableWidgetItem(str(diff['expected'])))
                table.setItem(i, 2, QTableWidgetItem(str(diff['actual'])))

            table.resizeColumnsToContents()
            layout.addWidget(table)

class MainWindow(QMainWindow):
    def __init__(self, camera_service, detector, storage_service, request_service):
        super().__init__()
        self.camera_service = camera_service
        self.detector = detector
        self.storage_service = storage_service
        self.request_service = request_service
        
        self.setup_ui()
        self.start_camera()

    def setup_ui(self):
        self.setWindowTitle("Ürün Tespit Sistemi")
        self.setGeometry(100, 100, 1200, 800)  # Pencereyi büyüttük

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget oluştur
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Kamera Tab'ı
        camera_tab = QWidget()
        camera_layout = QVBoxLayout(camera_tab)

        # Butonlar için yatay düzen
        buttons_layout = QHBoxLayout()
        
        # Koli Kapat butonu
        self.close_box_button = QPushButton("Koli Kapat")
        self.close_box_button.setFocusPolicy(Qt.StrongFocus)
        buttons_layout.addWidget(self.close_box_button)
        
        # Request Oluştur butonu
        create_request_button = QPushButton("Kameradan Request Oluştur")
        create_request_button.clicked.connect(self.create_request_from_camera)
        buttons_layout.addWidget(create_request_button)
        
        camera_layout.addLayout(buttons_layout)
        
        # Kamera görüntüsü
        self.camera_label = QLabel()
        camera_layout.addWidget(self.camera_label)

        self.tab_widget.addTab(camera_tab, "Kamera")

        # Koli Listesi Tab'ı
        list_tab = QWidget()
        list_layout = QHBoxLayout(list_tab)
        
        # Sol taraf - Koli listesi
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.box_list = QListWidget()
        self.box_list.setMinimumWidth(300)
        self.box_list.itemClicked.connect(self.show_box_details)
        left_layout.addWidget(self.box_list)
        
        # Silme butonunu koli listesi tab'ına taşıdık
        delete_box_button = QPushButton("Seçili Koliyi Sil")
        delete_box_button.clicked.connect(self.delete_box)
        left_layout.addWidget(delete_box_button)
        
        left_widget.setLayout(left_layout)
        list_layout.addWidget(left_widget, stretch=2)
        
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
        
        list_layout.addWidget(right_widget, stretch=3)

        self.tab_widget.addTab(list_tab, "Koli Listesi")

        # Kontrol Tab'ı
        control_tab = QWidget()
        control_layout = QHBoxLayout(control_tab)
        
        # Sol taraf - Request listesi
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Örnek request butonu ve silme butonu yan yana
        buttons_layout = QHBoxLayout()
        
        add_sample_button = QPushButton("Rastgele Request Ekle")
        add_sample_button.clicked.connect(self.add_sample_request)
        buttons_layout.addWidget(add_sample_button)
        
        delete_request_button = QPushButton("Seçili Request'i Sil")
        delete_request_button.clicked.connect(self.delete_request)
        buttons_layout.addWidget(delete_request_button)
        
        left_layout.addLayout(buttons_layout)
        
        self.request_list = QListWidget()
        self.request_list.setMinimumWidth(400)
        self.request_list.itemClicked.connect(self.show_request_details)
        left_layout.addWidget(self.request_list)
        
        # Request detayları
        self.request_details_label = QLabel()
        self.request_details_label.setAlignment(Qt.AlignTop)
        left_layout.addWidget(self.request_details_label)
        
        left_widget.setLayout(left_layout)
        control_layout.addWidget(left_widget)
        
        # Sağ taraf - Kontrol butonu
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.check_button = QPushButton("Kontrol Et")
        self.check_button.clicked.connect(self.check_request)
        right_layout.addWidget(self.check_button)
        right_layout.addStretch()
        
        control_layout.addWidget(right_widget)
        
        self.tab_widget.addTab(control_tab, "Kontrol")

        # Timer for camera updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~30fps

        # Button connections
        self.close_box_button.clicked.connect(self.close_box)

        # Koli Kapat butonuna otomatik focus
        self.close_box_button.setFocus()

        # Enter tuşunu Koli Kapat'a bağla
        self.close_box_button.setShortcut("Return")

        # Koli listesini yükle
        self.load_boxes()

        # Request listesini yükle
        self.load_requests()

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

    def close_box(self):
        box_id, ok = QInputDialog.getText(self, "Koli Numarası", 
                                        "Lütfen koli numarasını girin:")
        if ok and box_id:
            try:
                frame = self.camera_service.read_frame()
                # Tüm ürünleri tespit et
                all_products = self.detector.detect_products(frame)
                
                # Person olmayan ürünleri filtrele
                products = [p for p in all_products if p.name != 'person']
                
                if not products:
                    QMessageBox.warning(self, "Uyarı", "Kamerada geçerli ürün tespit edilemedi!")
                    return
                
                image_path = self.storage_service.save_image(frame, box_id, products)
                box = Box(id=box_id, products=products, image_path=image_path)
                self.storage_service.save_box(box)
                
                # Başarılı mesajı göster
                QMessageBox.information(self, 
                                      "Başarılı", 
                                      f"Koli #{box_id} başarıyla kaydedildi.\n"
                                      f"Tespit edilen ürün sayısı: {len(products)}")
                
                # Koli listesini güncelle
                self.load_boxes()
                
                # Koli Kapat butonuna tekrar focus ver
                self.close_box_button.setFocus()
                
            except Exception as e:
                QMessageBox.critical(self, 
                                   "Hata", 
                                   f"Koli kaydedilirken bir hata oluştu:\n{str(e)}")

    def start_camera(self):
        self.camera_service.start()

    def update_frame(self):
        try:
            frame = self.camera_service.read_frame()
            frame_copy = frame.copy()
            
            # Nesne tespiti
            products = self.detector.detect_products(frame)
            
            # Tespit edilen nesneleri çiz
            y_offset = 30
            for i, product in enumerate(products):
                # Debug bilgisi
                print(f"Tespit edilen: {product.name} (Güven: {product.confidence:.2f})")
                
                # Tespit edilen nesnenin konumunu al
                x, y, w, h = product.bbox  # bbox'ı Product sınıfına eklememiz gerekiyor
                
                # Çerçeve çiz
                cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # İsim ve güven değerini çerçevenin üstüne yaz
                text = f"{product.name} ({product.confidence:.2f})"
                cv2.putText(frame_copy, 
                           text,
                           (x, y - 5),  # Çerçevenin üstüne yaz
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5,  # Daha küçük font
                           (0, 255, 0), 
                           2)

            # Frame'i QLabel'a yerleştir
            height, width, channel = frame_copy.shape
            bytes_per_line = 3 * width
            frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            q_image = QImage(frame_copy.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(q_image))
            
        except Exception as e:
            print(f"Frame güncelleme hatası: {str(e)}") 

    def load_requests(self):
        requests = self.request_service.get_requests()
        self.request_list.clear()
        
        for req in requests:
            box = req['box']
            self.request_list.addItem(f"Koli: {box['number']} - {len(box['products'])} ürün")

    def check_request(self):
        current_item = self.request_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir request seçin!")
            return

        box_number = current_item.text().split(':')[1].split('-')[0].strip()
        
        # Request'i bul
        requests = self.request_service.get_requests()
        request = next((r for r in requests 
                       if r['box']['number'] == box_number), None)
        
        if not request:
            QMessageBox.warning(self, "Hata", "Request bulunamadı!")
            return

        # Gerçek koliyi bul
        boxes = self.storage_service.get_boxes()
        actual_box = next((b for b in boxes if b['id'] == box_number), None)
        
        if not actual_box:
            QMessageBox.warning(self, 
                              "Uyarı", 
                              f"Koli #{box_number} henüz taranmamış!")
            return

        # Karşılaştır
        request_box = BoxRequest.from_dict(request['box'])
        result = self.request_service.compare_box(request_box, actual_box)
        
        # Sonucu göster
        dialog = ComparisonDialog(result, self)
        dialog.exec_() 

    def add_sample_request(self):
        # Olası ürünler ve miktarları
        possible_products = [
            "laptop", "mouse", "keyboard", "monitor", 
            "cell phone", "tv", "remote", "book"
        ]
        
        # Rastgele 2-4 ürün seç
        product_count = randint(2, 4)
        selected_products = []
        
        for _ in range(product_count):
            product = {
                "name": choice(possible_products),
                "quantity": randint(1, 3)
            }
            selected_products.append(product)
        
        # Benzersiz koli numarası oluştur
        box_number = f"B{randint(1, 999):03d}"
        
        sample_request = Request.from_dict({
            "box": {
                "number": box_number,
                "products": selected_products
            }
        })
        
        self.request_service.save_request(sample_request)
        self.load_requests()

    def show_request_details(self, item):
        box_number = item.text().split(':')[1].split('-')[0].strip()
        
        requests = self.request_service.get_requests()
        request = next((r for r in requests 
                       if r['box']['number'] == box_number), None)
        
        if request:
            details = f"Koli: {request['box']['number']}\n\nÜrünler:\n"
            for product in request['box']['products']:
                details += f"• {product['name']} x{product['quantity']}\n"
            
            self.request_details_label.setText(details)

    def delete_box(self):
        current_item = self.box_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek koliyi seçin!")
            return

        box_id = current_item.text().split(' - ')[0].split(': ')[1]
        
        # Direkt sil, onay sorma
        self.storage_service.delete_box(box_id)
        # Listeyi güncelle
        self.load_boxes()
        # Görüntüyü ve ürün listesini temizle
        self.image_label.clear()
        self.products_label.clear()

    def delete_request(self):
        current_item = self.request_list.currentItem()
        if not current_item:
            return

        box_number = current_item.text().split(':')[1].split('-')[0].strip()
        
        # Direkt sil
        self.request_service.delete_request(box_number)
        self.load_requests()
        self.request_details_label.clear() 

    def create_request_from_camera(self):
        try:
            # Kameradan frame al
            frame = self.camera_service.read_frame()
            # Ürünleri tespit et (person'lar zaten filtrelenmiş olacak)
            products = self.detector.detect_products(frame)
            
            if not products:
                QMessageBox.warning(self, "Uyarı", "Kamerada ürün tespit edilemedi!")
                return
            
            # Ürünleri say (person hariç)
            product_counts = {}
            for product in products:
                if product.name != 'person':
                    # Her ürün için sayacı bir artır
                    product_counts[product.name] = product_counts.get(product.name, 0) + 1
            
            # Eğer person filtrelendikten sonra ürün kalmadıysa
            if not product_counts:
                QMessageBox.warning(self, "Uyarı", "Kamerada geçerli ürün tespit edilemedi!")
                return
            
            # Request oluştur
            box_number = f"R{randint(1, 999):03d}"
            request_products = [
                {"name": name, "quantity": count}  # Her ürün için gerçek sayısını kullan
                for name, count in product_counts.items()
            ]
            
            request = Request.from_dict({
                "box": {
                    "number": box_number,
                    "products": request_products
                }
            })
            
            # Request'i kaydet
            self.request_service.save_request(request)
            self.load_requests()
            
            # Kamera görüntüsünü kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.storage_service.images_dir, f"request_{box_number}_{timestamp}.jpg")
            cv2.imwrite(image_path, frame)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Request oluşturulurken hata: {str(e)}") 