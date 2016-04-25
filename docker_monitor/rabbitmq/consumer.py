# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import pika
from threading import Thread


def callback(ch, method, properties, body):
    print("[ {} ] Received {} {}".format(
        ch.channel_number, body, method.delivery_tag
    ))


class RabbitConsumer(Thread):
    """
    RabbitMQ Consumer class
    """

    def __init__(self, host, port, **kwargs):
        super(RabbitConsumer, self).__init__()

        self.kwargs = kwargs
        self.queue = kwargs['queue']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )

    def run(self):
        print ' [*] Waiting for messages. To exit press CTRL+C'
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_consume(
            callback, queue=self.queue, no_ack=True
        )
        channel.start_consuming()
