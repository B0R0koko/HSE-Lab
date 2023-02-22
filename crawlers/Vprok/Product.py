from dataclasses import dataclass

from typing import *


class Product:
    KEY_MAP = {
        "name": ["name"],
        "price": ["price"],
        "oldPrice": ["oldPrice"],
        "rating": ["rating"],
        "reviews": ["reviews"],
        "category": ["portal", "name"],
        "subcategory": ["category", "name"],
        "delivery_type": ["delivery", "lastMileType"],
        "express_available": ["delivery", "expressAvailable"],
        "courier_available": ["delivery", "courierAvailable"],
    }

    def __init__(self, data):
        self.data: Dict[str, Any] = self.parse(data)

    def nav_json(self, data: dict, key_list: List[str]) -> Union[Any, None]:
        for key in key_list:
            if data:
                if key in data:
                    data = data[key]
            else:
                return None
        return data

    def parse(self, data: dict) -> Dict[str, Any]:
        return {key: self.nav_json(data, val) for key, val in self.KEY_MAP.items()}
