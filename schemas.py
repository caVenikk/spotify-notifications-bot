from datetime import date
from enum import Enum
from pydantic import AnyUrl
from pydantic.dataclasses import dataclass


class Tariffs(Enum):
    individual = 'Индивидуальный'
    individual_discount = 'Индивидуальный (скидка)'
    family = 'Семейный'
    family_discount = 'Семейный (скидка)'
    free = 'Бесплатный'


@dataclass
class Subscriber:
    name: str
    surname: str
    link: AnyUrl
    spotify_nickname: str
    date: date
    tariff: Tariffs
    amount: int
    price: float

    @property
    def total(self):
        return self.amount * self.price

    def __repr__(self) -> str:
        return f'<b>{self.name}</b>: <i>{self.total}</i> rub ({self.date.strftime("%d.%m.%y")}) - {self.link}'

    def __str__(self) -> str:
        return f'<b>{self.name}</b>: <i>{self.total}</i> rub ({self.date.strftime("%d.%m.%y")}) - {self.link}'
