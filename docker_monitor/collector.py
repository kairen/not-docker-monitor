# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import argparse
import socket
import json
import sys
o

from docker_monitor.common import logs
from docker_monitor.common import config
from docker_monitor.common.decorator import align_terminal_top

from docker_monitor.meters import Meters
from docker_monitor.rabbitmq import publish, consumer

LOG = logging.getLogger("docker-monitor")
STATUS = dict()
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
        print("{id} Ports => {ports} CPU => {cpu:.2f}% Memory => {mem:0.2f} MB / {mem_total} MB = {mem_free:0.2f} MB".format(
            id=key,
            ports=value['ports'],
            cpu=value['cpu'],
            mem=value['memory'],
            mem_total=value['mem_total'],
            mem_free=value['mem_free']
        ))


def publish_status(meters):
    """
    Publish docker meters status callback
    """
    status = {
        socket.gethostname(): {
            "ip_addr": commands.getoutput("ip route get 8.8.8.8 | awk '{print $NF; exit}'"),
            "update_time": str(datetime.datetime.now()),
            "container_status":
                meters
        }
    }
    publish.RabbitPublish(
        host=CONF.rabbit_host(),
        port=CONF.rabbit_port(),
        queue=CONF.rabbit_queue(),
        body=json.dumps(status),
        user=CONF.rabbit_user(),
        passwd=CONF.rabbit_passwd(),
        timeout=CONF.rabbit_timeout(),
    ).run()


@align_terminal_top(description="Docker meter status")
def receive_callback(ch, method, properties, body):
    """
    RabbitMQ receive callback func
    """
    STATUS.update(json.loads(body))
    print(json.dumps(STATUS, indent=4, sort_keys=True))


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
    global CONF

    parser = get_parser()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    CONF = config.Configuration(args.config_file)
    if CONF.debug():
        sh = logging.StreamHandler()
        sh.setFormatter(logs.color_format())
        sh.setLevel(logging.WARNING)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(sh)
        sh.setLevel(logging.DEBUG)

    try:
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
