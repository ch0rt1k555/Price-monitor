from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    title: str
    price: Decimal
    currency: str
    url: str