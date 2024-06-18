from uuid import UUID
from random import choices, gauss
from models import Transaction, Agent, BankType
from typing import get_args, List


def transaction_generator(personList: List[Agent]) -> Transaction:
    persons = choices(personList, k=2)
    amount = round(abs(gauss(4, 10)) * 1000, 2)
    banks = choices(list(get_args(BankType)), [6, 2, 2, 2], k=2)
    return Transaction(
        ffrom=persons[0],
        to=persons[1],
        from_bankname=banks[0],
        to_bankname=banks[1],
        amount=amount,
    )
