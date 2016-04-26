# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import pika
import logging

LOG = logging.getLogger("consumer.meters")


def callback(ch, method, properties, body):
    print("[ {} ] Received {} {}".format(
        ch.channel_number, body, method.delivery_tag
    ))


class RabbitConsumer:
    """
    RabbitMQ Consumer class
    """

    def __init__(self, func, host, port, **kwargs):
        self.kwargs = kwargs
        self.queue = kwargs['queue']
        self.callback = func

        credentials = pika.PlainCredentials(kwargs['user'], kwargs['passwd'])
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                socket_timeout=kwargs['timeout']
            )
        )

    def start(self):
        print ' [*] Waiting for messages. To exit press CTRL+C'
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_consume(
            self.callback, queue=self.queue, no_ack=True
        )
        channel.start_consuming()


if __name__ == '__main__':
    RabbitConsumer(
        func=callback,
        host='10.26.1.113',
        port=5672,
        queue='stat',
        user='docker',
        passwd='docker',
        timeout=30,
    ).start()
