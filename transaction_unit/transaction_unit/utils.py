import time


def get_cur_time() -> str:
    return time.strftime("%H:%M:%S", time.gmtime())


def print_t(text: str) -> None:
    print(f"{get_cur_time()}::{text}")
