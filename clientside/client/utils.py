import time
import pandas

from typing import List
from models import Transaction


def get_cur_time() -> str:
    return time.strftime("%H:%M:%S", time.gmtime())


def print_t(text: str) -> None:
    print(f"{get_cur_time()}::{text}")


def print_result(list_tr: List[Transaction]) -> None:
    colums = ["UUID транзакции", "Отправитель", "Получатель", "Время выполнения"]
    dict_to_table = {}
    for col in colums:
        dict_to_table[col] = []

    for tr in list_tr:
        dict_to_table[colums[0]].append(str(tr.id)[0:6])
        dict_to_table[colums[1]].append(str(tr.ffrom)[0:6])
        dict_to_table[colums[2]].append(str(tr.to)[0:6])
        dict_to_table[colums[3]].append("%.2f" % (tr.proceed_time - tr.creation_time))
    print(pandas.DataFrame(dict_to_table))
