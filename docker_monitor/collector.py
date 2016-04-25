# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import commands
import argparse
import sys

from docker_monitor.common import logs
from docker_monitor.meters import Meters
from docker_monitor.common import config
from docker_monitor.common.decorator import align_terminal_top

LOG = logging.getLogger("docker-monitor")


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
        print("{container_id} CPU => {cpu:.2f}% Memory => {mem:0.2f} MB".format(
            container_id=key[0:12],
            cpu=value['cpu'],
            mem=value['memory']
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
        conf = config.Configuration(args.config_file)

        # Signal node monitor
        if conf.rabbit_role() == 'None':
            ids = container_ids()
            Meters(
                func=display_status,
                container_ids=ids,
                window_time=conf.window_time()
            ).run()

    except Exception as e:
        LOG.error("%s" % (e.__str__()))


if __name__ == '__main__':
    main()
