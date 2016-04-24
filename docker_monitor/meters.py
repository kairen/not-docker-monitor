# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import logging
import commands
import time
import multiprocessing
from threading import Thread

LOG = logging.getLogger("collect.meters")

SYS_CORE = multiprocessing.cpu_count()
SYS_CPU_CMD = "awk '/cpu / {for(i=2;i<=NF;i++) t+=$i; print t; t=0}' /proc/stat"


class Meters(Thread):
    """
    Docker CGroup meters class, this class is define all meters
    """

    CPU = 0x01
    MEMORY = 0x02
    ALL = 0x03

    _CGROUP_PATHS = {
        CPU: "/sys/fs/cgroup/cpuacct/docker",
        MEMORY: "/sys/fs/cgroup/memory/docker",
    }

    _CGROUP_FILE = {
        CPU: "cpuacct.usage",
        MEMORY: "memory.usage_in_bytes"
    }

    def __init__(self, func, **kwargs):
        super(Meters, self).__init__()

        self.kwargs = kwargs
        self.container_ids = self.kwargs['container_ids']

        self.callback = func

        self.f_usage = dict()
        self.l_usage = dict()

    def _get_usages(self):
        usages = dict()
        sys_cpu_usage = int(commands.getoutput(SYS_CPU_CMD))

        for container_id in self.container_ids:
            usages[container_id] = {}
            for (key, path_v), (_, file_v) in zip(
                    Meters._CGROUP_PATHS.items(),
                    Meters._CGROUP_FILE.items()
            ):
                path = "{path}/{id}/{file_name}".format(
                    path=path_v,
                    id=container_id,
                    file_name=file_v,
                )
                with open(path, 'r') as f:
                    if key == Meters.CPU:
                        usages[container_id].update({
                            'sys_cpu': sys_cpu_usage,
                            'cgroup_cpu': int(f),
                        })
                    else:
                        usages[container_id].update({'cgroup_memory': int(f)})

        return usages

    def calc_cpu_usage(self, first, last):
        sys_diff = (last['sys_cpu'] != first['sys_cpu'])
        cgroup_diff = (last['cgroup_cpu'] != first['cgroup_cpu'])

        if sys_diff and cgroup_diff:
            cpu_total = last['sys_cpu'] - first['sys_cpu']
            cgroup_total = last['cgroup_cpu'] - first['cgroup_cpu']
            return cgroup_total * SYS_CORE / cpu_total * 100 / float(10000000)
        else:
            return None

    def calc_mem_usage(self, last):
        return last['cgroup_memory'] / float(1000000)

    def get_usage_rate(self):
        rates = dict()
        for container_id in self.container_ids:
            first = self.f_usage[container_id]
            last = self.l_usage[container_id]

            mem_rate = self.calc_mem_usage(last)
            cpu_rate = self.calc_cpu_usage(first, last)
            if cpu_rate:
                self.f_usage[container_id] = self.l_usage[container_id]
            rates[container_id].update({'cpu': cpu_rate, 'memory': mem_rate})

        return rates

    def run(self):
        while True:
            try:
                usages = self._get_usages()
                if len(self.f_usage) == 0 and len(usages) != len(self.f_usage):
                    self.f_usage = usages
                else:
                    self.l_usage = usages
                    rates = self.get_usage_rate()
                    if rates:
                        self.callback(rates)

            except Exception as e:
                LOG.error("%s" % (e.__str__()))

            time.sleep(0.5)
