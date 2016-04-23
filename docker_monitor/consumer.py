# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.99.100')
)
channel = connection.channel()

channel.queue_declare(queue='hello')

print ' [*] Waiting for messages. To exit press CTRL+C'


def callback(ch, method, properties, body):
    print("[ {} ] Received {} {}".format(
        ch.channel_number, body, method.delivery_tag
    ))

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

channel.start_consuming()