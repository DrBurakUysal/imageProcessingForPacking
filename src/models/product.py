from dataclasses import dataclass

@dataclass
class Product:
    name: str
    confidence: float
    bbox: list = None

    def __init__(self, name: str, confidence: float, bbox: list = None):
        self.name = name
        self.confidence = confidence
        self.bbox = bbox or [0, 0, 0, 0]  # x, y, w, h

    def to_dict(self):
        return {
            'name': self.name,
            'confidence': self.confidence,
            'bbox': self.bbox
        } 