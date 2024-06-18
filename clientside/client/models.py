import time
from pydantic import BaseModel, Field, PrivateAttr
from uuid import uuid4, UUID
from typing import Literal


from russian_names import RussianNames

BankType = Literal["Сбер", "ВТБ", "Тинькофф", "Альфабанк"]
namesGenerator = RussianNames(patronymic=False)


class Agent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(default_factory=namesGenerator.get_person)

    def __str__(self) -> str:
        return f"{str(self.id)[0:6]} - {self.name}"


class Transaction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    ffrom: Agent
    from_bankname: BankType
    to: Agent
    to_bankname: BankType
    amount: float
    creation_time: float = Field(default_factory=time.time)
    proceed_time: float = 0

    def __str__(self) -> str:
        return f"id: {str(self.id)[0:6]}\t| from:{str(self.ffrom)[0:6]} - to:{str(self.to)[0:6]} - amount:{self.amount}"

    def mark_as_completed(self) -> None:
        self.proceed_time = time.time()


class TransactionStatus(BaseModel):
    id: UUID
    status: Literal["OK", "ERROR"]
    unit_id: int
    transaction: Transaction
