# Ürün Tespit ve Paketleme Kontrol Sistemi

Bu proje, YOLOv3 nesne tespit modeli kullanarak paketleme sürecinde ürün tespiti ve kontrolü yapan bir masaüstü uygulamasıdır.

## Özellikler

- Gerçek zamanlı ürün tespiti
- Koli içeriği kaydetme ve listeleme
- Request (talep) oluşturma ve kontrol etme
- Kamera görüntüsü üzerinde tespit edilen nesnelerin görselleştirilmesi
- Koli içeriği ile talep karşılaştırma

## Gereksinimler

- Python 3.7+
- OpenCV
- PyQt5
- NumPy
- YOLOv3 model dosyaları:
  - yolov3.weights
  - yolov3.cfg
  - coco.names

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```
pip install -r requirements.txt
2. YOLOv3 model dosyalarını indirin:
- [yolov3.weights](https://pjreddie.com/media/files/yolov3.weights)
- [yolov3.cfg](https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg)
- [coco.names](https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names)

3. İndirilen model dosyalarını `data/weights/` klasörüne yerleştirin.

## Kullanım

1. Uygulamayı başlatın:
```

2. Ana pencerede üç sekme bulunur:
   - **Kamera**: Canlı kamera görüntüsü ve ürün tespiti
   - **Koli Listesi**: Kaydedilen kolilerin listesi ve detayları
   - **Kontrol**: Request oluşturma ve koli kontrolü

### Koli Kaydetme
1. "Kamera" sekmesinde "Koli Kapat" butonuna tıklayın
2. Koli numarasını girin
3. Sistem otomatik olarak kamerada görünen ürünleri tespit edip kaydedecektir

### Request Oluşturma ve Kontrol
1. "Kontrol" sekmesinde "Rastgele Request Ekle" ile test talebi oluşturabilir veya "Kameradan Request Oluştur" ile mevcut görüntüden talep oluşturabilirsiniz
2. Bir request seçin ve "Kontrol Et" butonuna tıklayın
3. Sistem, seçili request ile taranan koliyi karşılaştırıp sonucu gösterecektir

## Proje Yapısı
```
├── data/
│   ├── storage/         # Koli ve request verileri
│   └── weights/         # YOLOv3 model dosyaları
├── src/
│   ├── detection/       # Nesne tespit modülleri
│   ├── models/         # Veri modelleri
│   ├── services/       # Servis sınıfları
│   └── ui/            # Kullanıcı arayüzü
├── main.py            # Ana uygulama
└── requirements.txt   # Bağımlılıklar
```

## Hata Giderme

- Eğer kamera başlatılamazsa, `main.py` dosyasında kamera ID'sini kontrol edin
- Model dosyaları eksikse, uygulama başlangıçta uyarı verecek ve indirme linklerini gösterecektir
- Görüntü işleme performansı için yeterli RAM ve işlemci gücü gereklidir

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.