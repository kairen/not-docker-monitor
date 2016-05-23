# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging

from docker_monitor.common import info
from docker_monitor.meters import base_meters


LOG = logging.getLogger("collect.sys.meters")


class SysMeters(base_meters.Meters):
    """
    System meters class, this class is define all meters
    """

    def _get_usages(self):
        return {"cpu_total": info.cpu_total(), "cpu_idle": info.cpu_idle()}

    def calc_cpu_usage(self, first, last):
        total_diff = (last['cpu_total'] != first['cpu_total'])
        idle_diff = (last['cpu_idle'] != first['cpu_idle'])

        if total_diff and idle_diff:
            total = last['cpu_total'] - first['cpu_total']
            idle = last['cpu_idle'] - first['cpu_idle']
            return float(100) - (idle / total * 100)
        else:
            return None

    def get_usage_rate(self):
        cpu_rate = self.calc_cpu_usage(self.first_usage, self.last_usage)
        return {
            "cpu_used": cpu_rate,
            "cpu_MHz": info.cpu_speed,
            "mem_used": info.mem_used(),
            "mem_total": info.mem_total(),
            "mem_free": info.mem_free(),
        } if cpu_rate else None

    def get_rates(self, callback_rates):
        usage = self._get_usages()

        if len(set(self.first_usage.keys()) ^ set(usage.keys())) != 0:
            self.first_usage = usage
        else:
            self.last_usage = usage
            rates = self.get_usage_rate()
            if rates:
                callback_rates.update(rates)
                self.callback(callback_rates)
