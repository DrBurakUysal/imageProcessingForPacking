import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.detection.yolo_detector import YOLODetector
from src.services.camera_service import CameraService
from src.services.storage_service import StorageService
from src.services.request_service import RequestService

def check_yolo_files(weights_path, config_path, classes_path):
    missing_files = []
    if not os.path.exists(weights_path):
        missing_files.append(f"weights dosyası bulunamadı: {weights_path}")
    if not os.path.exists(config_path):
        missing_files.append(f"config dosyası bulunamadı: {config_path}")
    if not os.path.exists(classes_path):
        missing_files.append(f"classes dosyası bulunamadı: {classes_path}")
    
    if missing_files:
        print("\nEksik YOLO dosyaları:")
        for file in missing_files:
            print(f"- {file}")
        print("\nLütfen eksik dosyaları indirin:")
        print("weights: https://pjreddie.com/media/files/yolov3.weights")
        print("cfg: https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg")
        print("coco names: https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names")
        sys.exit(1)

def main():
    try:
        # Yolları yapılandır
        base_dir = os.path.dirname(os.path.abspath(__file__))
        weights_path = os.path.join(base_dir, 'data', 'weights', 'yolov3.weights')
        config_path = os.path.join(base_dir, 'data', 'weights', 'yolov3.cfg')
        classes_path = os.path.join(base_dir, 'data', 'weights', 'coco.names')
        storage_dir = os.path.join(base_dir, 'data', 'storage')

        # YOLO dosyalarını kontrol et
        check_yolo_files(weights_path, config_path, classes_path)

        # Servisleri başlat
        print("YOLOv3 yükleniyor...")
        detector = YOLODetector(weights_path, config_path, classes_path)
        print("Kamera başlatılıyor...")
        camera_service = CameraService()
        storage_service = StorageService(storage_dir)
        request_service = RequestService(storage_dir)

        # UI'ı başlat
        print("Uygulama başlatılıyor...")
        app = QApplication(sys.argv)
        window = MainWindow(camera_service, detector, storage_service, request_service)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"\nKritik hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 