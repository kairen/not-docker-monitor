# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import argparse
import json
import logging

from docker_monitor.common import info
from docker_monitor.common import config
from docker_monitor.common import logs
from docker_monitor.common.decorator import align_terminal_top
from docker_monitor.meters.docker_meters import DockerMeters
from docker_monitor.meters.sys_mteres import SysMeters
from docker_monitor.rabbitmq import publish, consumer

LOG = logging.getLogger("docker-monitor")
STATUS = dict()
CONF = None

DISPLAY_CPU = "CPU => {cpu:.2f}% "
DISPLAY_MEM = "Memory => {mem:0.2f} MB / {mem_total} MB = {mem_free:0.2f} MB"

DISPLAY_MESSAGE = "{id} Ports => {ports} " + DISPLAY_CPU + DISPLAY_MEM


@align_terminal_top(description="Docker meter status")
def display_status(meters, t):
    """
    Display docker meters status callback
    :param t: meter type
    :param meters: this is docker meter objects
    :return: if meter not None return status,
             else return some message
    """
    if t == 'cgroup':
        for key, value in meters.iteritems():
            print(DISPLAY_MESSAGE.format(
                id=key, ports=value['ports'],
                cpu=value['cpu_used'], mem=value['mem_used'],
                mem_total=value['mem_total'], mem_free=value['mem_free']
            ))


def publish_system(meters, t):
    """
    Publish system meters status callback
    """
    status = info.status(t, meters)
    publish.RabbitPublish(body=json.dumps(status), **CONF.rabbit_profile()).run()


def publish_container(meters, t):
    """
    Publish container meters status callback
    """
    status = info.status(t, meters)
    publish.RabbitPublish(body=json.dumps(status), **CONF.rabbit_profile()).run()


@align_terminal_top(description="Docker meter status")
def receive_callback(ch, method, properties, body):
    """
    RabbitMQ receive callback func
    """
    for k, v in json.loads(body).items():
        if k not in STATUS:
            STATUS.update(json.loads(body))

        STATUS[k].update(v)
    data = json.dumps(STATUS, indent=4, sort_keys=True)
    with open(CONF.save_path(), "w") as f:
        f.write(data)
        f.close()
    print(data)


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
        role = CONF.rabbit_profile()["role"]
        if role == 'consumer':
            consumer.RabbitConsumer(
                func=receive_callback,
                **CONF.rabbit_profile()
            ).start()
        else:
            docker_cbf = display_status if role == 'None' else publish_container
            sys_cbf = display_status if role == 'None' else publish_system
            dt = DockerMeters(func=docker_cbf, window_time=CONF.window_time())
            dt.start()
            st = SysMeters(func=sys_cbf, window_time=CONF.window_time())
            st.start()
            threads = [dt, st]
            while True:
                for t in threads:
                    t.join(10)
                    if not t.isAlive():
                        break
    except Exception as e:
        LOG.error("%s" % (e.__str__()))
