import json
import os
from typing import List, Optional
from ..models.request import Request, BoxRequest

class RequestService:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.requests_file = os.path.join(storage_dir, 'requests.json')
        
        if not os.path.exists(self.requests_file):
            with open(self.requests_file, 'w') as f:
                json.dump([], f)

    def save_request(self, request: Request):
        requests = self.get_requests()
        requests.append({
            'box': {
                'number': request.box.number,
                'products': [{'name': p.name, 'quantity': p.quantity} 
                           for p in request.box.products]
            }
        })
        
        with open(self.requests_file, 'w') as f:
            json.dump(requests, f)

    def get_requests(self) -> List[dict]:
        with open(self.requests_file, 'r') as f:
            return json.load(f)

    def compare_box(self, request_box: BoxRequest, actual_box: dict) -> dict:
        """Request ile gerçek koli verilerini karşılaştır"""
        result = {
            'matching': True,
            'differences': []
        }

        # Request'teki ürünleri say
        request_products = {}
        for product in request_box.products:
            request_products[product.name] = product.quantity

        # Gerçek kolideki ürünleri say
        actual_products = {}
        for product in actual_box['products']:
            name = product['name']
            actual_products[name] = actual_products.get(name, 0) + 1

        # Karşılaştır
        all_products = set(request_products.keys()) | set(actual_products.keys())
        
        for product in all_products:
            req_count = request_products.get(product, 0)
            act_count = actual_products.get(product, 0)
            
            if req_count != act_count:
                result['matching'] = False
                result['differences'].append({
                    'product': product,
                    'expected': req_count,
                    'actual': act_count
                })

        return result 

    def delete_request(self, box_number: str):
        requests = self.get_requests()
        
        # Request'i listeden çıkar
        requests = [r for r in requests if r['box']['number'] != box_number]
        
        # Güncellenmiş listeyi kaydet
        with open(self.requests_file, 'w') as f:
            json.dump(requests, f) 