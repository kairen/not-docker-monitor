# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import commands
from docker_monitor.common import logs
from docker_monitor.common.decorator import align_terminal_top
from docker_monitor.meters import Meters

LOG = logging.getLogger("collect")


def container_ids():
    """
    Get docker all container long id
    :return: container id list
    """
    return commands.getoutput("docker ps -q --no-trunc").split("\n")


@align_terminal_top(description="Docker meter status")
def display_status(meters):
    """
    Display docker meters status
    :param meters: this is docker meter objects
    :return: if meter not None return status,
             else return some message
    """

    for key, value in meters.iteritems():
        print("{container_id} CPU => {cpu:.2f} % Memory => {mem:0.2f} MB".format(
            container_id=key[1:12],
            cpu=value['cpu'],
            mem=value['memory']
        ))


def main():
    # conf = config.Configuration(config.FILE_PATH)

    sh = logging.StreamHandler()
    sh.setFormatter(logs.color_format())
    sh.setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(sh)
    sh.setLevel(logging.DEBUG)

    ids = container_ids()

    Meters(
        func=display_status,
        container_ids=ids
    ).run()


if __name__ == '__main__':
    main()
