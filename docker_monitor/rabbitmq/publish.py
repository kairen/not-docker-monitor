# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import pika
from threading import Thread


class RabbitPublish(Thread):
    """
    RabbitMQ Publish class
    """

    def __init__(self, host, port, **kwargs):
        super(RabbitPublish, self).__init__()

        self.kwargs = kwargs
        self.queue = kwargs['queue']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )

    def run(self):
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_publish(
            exchange='', routing_key='hello', body='Hello World!'
        )
        print " [x] Sent 'Hello World!'"
        # self.connection.close()
