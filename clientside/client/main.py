import aio_pika
import logging
import argparse

from typing import List
from dataclasses import dataclass

from rabbitmq_testclient import RabbitMQClient
from models import Agent, Transaction, TransactionStatus
from transaction_generator import transaction_generator
from utils import print_t, print_result

publishing_host = "localhost"
publishing_port = 3494
app_name = "TransactionEmiter"
send_queue = "transaction.send"
recieve_queue = "transaction.status"
logger = logging.getLogger(name="main")
app: RabbitMQClient = None
agents_list: List[Agent] = [Agent() for _ in range(15)]
curupdate = 0
max_update = -1


@dataclass
class Records:
    not_sent_rec = dict()
    sent_and_rec = dict()
    sent_not_rec = dict()


records = Records()


async def print_callback(app: RabbitMQClient, text: aio_pika.abc.AbstractIncomingMessage):
    ans = TransactionStatus.model_validate_json(text.body.decode())
    print_t(f"Transaction {ans.id} handled by {ans.unit_id}!")
    trans = ans.transaction
    if trans.id in records.sent_not_rec:
        del records.sent_not_rec[trans.id]
        records.sent_and_rec[trans.id] = trans
    else:
        records.not_sent_rec[trans.id] = trans


async def init(app: RabbitMQClient):
    await app.subscribe_to_queue(recieve_queue, print_callback, auto_clear=True)
    if max_update != -1:
        for _ in range(max_update):
            generated_transaction = transaction_generator(agents_list)
            await app.post(send_queue, generated_transaction.model_dump_json().encode())
            print_t(f"Transaction {generated_transaction}")
            records.sent_not_rec[generated_transaction.id] = generated_transaction


async def update(app):
    message = transaction_generator(agents_list)
    await app.post(send_queue, message.model_dump_json().encode())
    print_t(f"Transaction {message}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "perf",
        type=int,
        help="С какой скоростью будут генерироваться транзакции."
        "Напрмер, при мощности 60 клиент будет генерировать одну транзакцию каждую секунд"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Сколько транзакций нужно сгенерировать"
    )
    args = parser.parse_args()
    dt = 60 / float(args.perf)
    if args.limit:
        max_update = args.limit
    else:
        max_update = -1
    try:
        app = RabbitMQClient(
            host=publishing_host,
            port=publishing_port,
            appname=app_name,
            dt=dt,
            init_func=init,
            process_func=update if max_update == -1 else None,
            exchange_name="transactions"
        )
    except KeyboardInterrupt:
        pass
    finally:
        if records.not_sent_rec:
            print()
            print("//////Транзакции отправленные ранее\\\\\\\\\\\\")
            print_result([records.not_sent_rec[rec] for rec in records.not_sent_rec])
        if records.sent_and_rec:
            print()
            print("//////Транзакции отправленные и обработанный сейчас\\\\\\\\\\\\")
            print_result([records.sent_and_rec[rec] for rec in records.sent_and_rec])
        if records.sent_not_rec:
            print()
            print("//////Транзакции отправленные, но не обработанные\\\\\\\\\\\\")
            print_result([records.sent_not_rec[rec] for rec in records.sent_not_rec])
    print_t("Exited!")
