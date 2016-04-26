# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import pika
import logging
import datetime

from threading import Thread

LOG = logging.getLogger("publish.meters")


class RabbitPublish(Thread):
    """
    RabbitMQ Publish class
    """

    def __init__(self, host, port, **kwargs):
        super(RabbitPublish, self).__init__()

        self.kwargs = kwargs
        self.queue = self.kwargs['queue']

        credentials = pika.PlainCredentials(kwargs['user'], kwargs['passwd'])
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                socket_timeout=kwargs['timeout']
            )
        )

    def run(self):
        try:
            channel = self.connection.channel()
            channel.queue_declare(self.queue)
            channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=self.kwargs['body']
            )
            LOG.debug("{time} - {body}".format(
                time=datetime.datetime.now(),
                body=self.kwargs['body']
            ))
            self.connection.close()
        except Exception as e:
            LOG.error("%s" % (e.__str__()))


if __name__ == '__main__':
    import json
    d = {'1234': '143', 'asd': 1}
    RabbitPublish(
        host='10.26.1.113',
        port=5672,
        queue='stat',
        body=json.dumps(d),
        user='docker',
        passwd='docker',
        timeout=30,
    ).run()
