# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import argparse
import socket
import json
import sys

from docker_monitor.common import logs
from docker_monitor.common import config
from docker_monitor.common.decorator import align_terminal_top

from docker_monitor.meters import Meters
from docker_monitor.rabbitmq import publish, consumer

LOG = logging.getLogger("docker-monitor")
CONF = None


@align_terminal_top(description="Docker meter status")
def display_status(meters):
    """
    Display docker meters status callback
    :param meters: this is docker meter objects
    :return: if meter not None return status,
             else return some message
    """
    for key, value in meters.iteritems():
        print("{container_id} CPU => {cpu:.2f}% Memory => {mem:0.2f} MB".format(
            container_id=key[0:12],
            cpu=value['cpu'],
            mem=value['memory']
        ))


def publish_status(meters):
    """
    Publish docker meters status callback
    """
    status = {socket.gethostname(): meters}
    publish.RabbitPublish(
        host=CONF.rabbit_host(),
        port=CONF.rabbit_port(),
        queue=CONF.rabbit_queue(),
        body=json.dumps(status),
        user=CONF.rabbit_user(),
        passwd=CONF.rabbit_passwd(),
        timeout=CONF.rabbit_timeout(),
    ).run()


def receive_callback(ch, method, properties, body):
    """
    RabbitMQ receive callback func
    """
    print("[ {} ] Received : {} ".format(
        ch.channel_number, body
    ))


def get_parser():
    """
    Command line interface args parser
    :rtype: parser object
    """
    parser = argparse.ArgumentParser(
        prog='docker-monitor',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Collecting docker meters',
    )

    parser.add_argument("--config-file", help="Configuration file path")

    return parser


def main():
    """
    Docker monitor entry point ...
    """
    sh = logging.StreamHandler()
    sh.setFormatter(logs.color_format())
    sh.setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(sh)
    sh.setLevel(logging.DEBUG)

    parser = get_parser()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    try:
        global CONF
        CONF = config.Configuration(args.config_file)
        role = CONF.rabbit_role()

        if role == 'consumer':
            consumer.RabbitConsumer(
                func=receive_callback,
                host=CONF.rabbit_host(),
                port=CONF.rabbit_port(),
                queue=CONF.rabbit_queue(),
                user=CONF.rabbit_user(),
                passwd=CONF.rabbit_passwd(),
                timeout=CONF.rabbit_timeout(),
            ).start()
        else:
            Meters(
                func=display_status if role == 'None' else publish_status,
                window_time=CONF.window_time()
            ).run()

    except Exception as e:
        LOG.error("%s" % (e.__str__()))
