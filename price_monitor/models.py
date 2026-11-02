from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    id: int
    title: str
    currency: str
    price: Decimal
    url: str