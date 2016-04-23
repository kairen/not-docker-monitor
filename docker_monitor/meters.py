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

    _CGROUP_PATHS = {
        CPU: "/sys/fs/cgroup/cpuacct/docker",
        MEMORY: "/sys/fs/cgroup/memory/docker"
    }

    _CGROUP_FILE = {
        CPU: "cpuacct.usage",
        MEMORY: "memory.usage_in_bytes"
    }

    def __init__(self, func, meter_type, **kwargs):
        super(Meters, self).__init__()

        self.kwargs = kwargs
        self.container_ids = self.kwargs['container_ids']
        self.meter_type = meter_type
        self.path = Meters._CGROUP_PATHS[meter_type]
        self.file = Meters._CGROUP_FILE[meter_type]

        self.callback = func

        self.f_usage = dict()
        self.l_usage = dict()

    def _get_usages(self):
        usages = dict()
        for container_id in self.container_ids:
            path = "{path}/{id}/{file_name}".format(
                path=self.path,
                id=container_id,
                file_name=self.file
            )
            with open(path, 'r') as f:
                usages[container_id] = int(f.read())

        return usages

    def _get_cpu_usage(self):
        sys_cpu_usage = int(commands.getoutput(SYS_CPU_CMD))
        status = dict()

        for identity, usage in self._get_usages().iteritems():
            status[identity] = {
                'sys_usage': sys_cpu_usage,
                'cgroup_usage': usage,
            }

        return status

    def _get_mem_usage(self):
        status = dict()
        for identity, usage in self._get_usages().iteritems():
            status[identity] = {'cgroup_usage': usage}

        return status

    def calc_cpu_usage(self):
        cpu_rates = dict()
        for identity in self.container_ids:
            f_usage = self.f_usage[identity]
            l_usage = self.l_usage[identity]

            sys_diff = (l_usage['sys_usage'] != f_usage['sys_usage'])
            cgroup_diff = (l_usage['cgroup_usage'] != f_usage['cgroup_usage'])

            if sys_diff and cgroup_diff:
                cpu_total = l_usage['sys_usage'] - f_usage['sys_usage']
                cgroup_total = l_usage['cgroup_usage'] - f_usage['cgroup_usage']
                rate = cgroup_total * SYS_CORE / cpu_total * 100
                cpu_rates[identity] = rate / float(10000000)
                self.f_usage[identity] = self.l_usage[identity]

        return cpu_rates

    def run(self):
        while True:
            try:
                usages = self._get_cpu_usage()
                if len(self.f_usage) == 0 and len(usages) != len(self.f_usage):
                    self.f_usage = usages
                else:
                    self.l_usage = usages
                    cpu_rates = self.calc_cpu_usage()
                    if cpu_rates:
                        self.callback(cpu_rates)

            except Exception as e:
                LOG.error("%s" % (e.__str__()))

            time.sleep(0.1)
