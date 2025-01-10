from abc import ABC, abstractmethod
from typing import List
from ..models.product import Product

class ObjectDetector(ABC):
    @abstractmethod
    def detect_box(self, frame) -> bool:
        pass

    @abstractmethod
    def detect_products(self, frame) -> List[Product]:
        pass 