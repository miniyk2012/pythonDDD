from __future__ import annotations
from typing import Optional, Set, List
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
        self._purchased_quantitiry = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __gt__(self, other: Batch):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self):
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantitiry - self.allocated_quantity


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    for batch in sorted(batches):
        if batch.can_allocate(line):
            batch.allocate(line)
            break
    return batch.reference
