from dataclasses import dataclass
from datetime import datetime
from typing import List
from .product import Product

@dataclass
class Box:
    id: str
    products: List[Product]
    image_path: str
    timestamp: datetime = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'products': [p.to_dict() for p in self.products],
            'image_path': self.image_path,
            'timestamp': self.timestamp.isoformat()
        } 