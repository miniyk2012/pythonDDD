from typing import Optional
from dataclasses import dataclass

from datetime import date


@dataclass(frozen=True)  # 对字段赋值将会产生异常, 模拟了只读的冻结实例
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    def allocate(self, line: OrderLine):
        self.available_quantity -= line.qty

    def can_allocate(self, small_line: OrderLine) -> bool:
        return self.sku == small_line.sku and self.available_quantity >= small_line.qty
