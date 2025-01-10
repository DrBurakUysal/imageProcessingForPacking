from dataclasses import dataclass
from typing import List

@dataclass
class RequestProduct:
    name: str
    quantity: int

@dataclass
class BoxRequest:
    number: str
    products: List[RequestProduct]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            number=data['number'],
            products=[RequestProduct(**p) for p in data['products']]
        )

@dataclass
class Request:
    box: BoxRequest

    @classmethod
    def from_dict(cls, data: dict):
        return cls(box=BoxRequest.from_dict(data['box'])) 