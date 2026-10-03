from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    title: str
    url: str
    price: Decimal
    currency: str