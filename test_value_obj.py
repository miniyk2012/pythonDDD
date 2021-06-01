from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


@dataclass
class D:
    x: List = field(default_factory=list)

    def add(self, element):
        self.x += element


class Person:
    def __init__(self, id_, name: Name):
        self.id_ = id_
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False

        return other.id_ == self.id_

    def __hash__(self):
        return hash(self.id_)


def test_barry_is_harry():
    harry = Person(1, Name("Harry", "Percival"))
    barry = Person(1, Name("Barry", "Percival"))
    barry.name = Name("Barry", "Percival")
    assert harry == barry

    s = set()
    s.add(harry)
    s.add(barry)
    assert len(s) == 1


def test_field():
    a = D()
    b = D()
    assert a.x is not b.x
    a.add([10])
    assert a.x is not b.x
