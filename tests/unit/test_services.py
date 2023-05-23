from unittest import mock

import pytest

from allocation.service_layer import services, unit_of_work
from allocation.service_layer.unit_of_work import EventsUnitOfWork


class FakeRepository:
    def __init__(self, products):
        self.seen = set()  # type: Set[model.Product]
        self._products = set(products)

    def add(self, product):
        self.seen.add(product)
        self._products.add(product)

    def get(self, sku):
        product = next((p for p in self._products if p.sku == sku), None)
        if product:
            self.seen.add(product)
        return product


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch_for_new_product():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.uow.committed


def test_add_batch_for_existing_product():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("b1", "GARISH-RUG", 100, None, uow)
    services.add_batch("b2", "GARISH-RUG", 99, None, uow)
    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.uow.committed


def test_sends_email_on_out_of_stock_error():
    uow = EventsUnitOfWork(FakeUnitOfWork())
    services.add_batch("b1", "POPULAR-CURTAINS", 9, None, uow)

    with mock.patch("allocation.adapters.email.send_mail") as mock_send_mail:
        services.allocate("o1", "POPULAR-CURTAINS", 10, uow)
        assert mock_send_mail.call_args == mock.call(
            "stock@made.com",
            f"Out of stock for POPULAR-CURTAINS",
        )
