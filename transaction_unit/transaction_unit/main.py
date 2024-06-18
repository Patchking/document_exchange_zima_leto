import aio_pika
import time
import logging
import asyncio
import argparse

from typing import List

from rabbitmq_testclient import RabbitMQClient
from models import Agent, Transaction, TransactionStatus
from utils import print_t

publishing_host = "localhost"
publishing_port = 3494
unit_id: int = 0
app_name = "TransactionEmiter"
send_queue = "transaction.status"
recieve_queue = "transaction.send"
handling_time = 5.0
logger = logging.getLogger(name="main")
app: RabbitMQClient = None


async def handle_transaction(app: RabbitMQClient, text: aio_pika.abc.AbstractIncomingMessage):
    await text.ack()
    transaction: Transaction = Transaction.model_validate_json(text.body.decode())
    print_t(f"Got transaction {str(transaction.id)[0:6]}.")
    await asyncio.sleep(handling_time)
    transaction.mark_as_completed()
    transaction_status = TransactionStatus(
        id=transaction.id,
        status="OK",
        unit_id=unit_id,
        transaction=transaction
    )
    await app.post(send_queue, transaction_status.model_dump_json().encode())
    print_t(f"Transaction {str(transaction.id)[0:6]} and sent back!")


async def init(app: RabbitMQClient):
    await app.subscribe_to_queue(recieve_queue, handle_transaction)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "perf",
        type=int,
        help="Определяет мощность обрабатывающего юинта в операциях в минуты."
        "Напрмер, при мощности 10 юнит будет обрабатывать одну транзакцию каждые 6 секунд"
    )
    parser.add_argument(
        "id",
        type=int,
        help="Номре обрабатывающего юнита"
    )
    args = parser.parse_args()
    handling_time = 60 / float(args.perf)
    unit_id = args.id
    app = RabbitMQClient(
        host=publishing_host,
        port=publishing_port,
        appname=app_name,
        dt=5.0,
        init_func=init,
        process_func=None,
        exchange_name="transactions"
    )
