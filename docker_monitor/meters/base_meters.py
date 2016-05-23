# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import time

from threading import Thread
from abc import ABCMeta, abstractmethod

LOG = logging.getLogger("collect.docker.meters")


class Meters(Thread):
    """
    Base meters class, this class is define all meters
    """

    CPU = 0x01
    MEMORY = 0x02

    def __init__(self, func, **kwargs):
        super(Meters, self).__init__()

        self.kwargs = kwargs

        window_time = self.kwargs['window_time']
        self.window_time = window_time if window_time else 0.5
        self.container_ids = None
        self.callback = func

        self.first_usage = dict()
        self.last_usage = dict()

    @abstractmethod
    def _get_usages(self):
        pass

    @abstractmethod
    def calc_cpu_usage(self, first, last):
        pass

    @abstractmethod
    def get_usage_rate(self):
        pass

    @abstractmethod
    def get_rates(self, callback_rates):
        pass

    def run(self):
        callback_rates = dict()
        while True:
            try:
                self.get_rates(callback_rates)
            except Exception as e:
                LOG.error("%s" % (e.__str__()))

            time.sleep(self.window_time)