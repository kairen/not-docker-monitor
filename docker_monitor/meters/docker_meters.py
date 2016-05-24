# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved


import logging

from docker_monitor.common import info
from docker_monitor.meters import base_meters

LOG = logging.getLogger("collect.docker.meters")


class DockerMeters(base_meters.Meters):
    """
    Docker meters class, this class is define all meters
    """

    def _get_usages(self):
        usages = dict()

        for cid in self.container_ids:
            sys_mem = info.mem_total()
            cgroup_mem = info.cgroup_limit_mem(cid)
            mem = sys_mem if sys_mem < cgroup_mem else cgroup_mem
            usages[cid] = {
                "cpu_sys": info.cpu_total(),
                "cpu_cgroup": info.cgroup_cpu_usage(cid),
                "mem_total": mem,
                "mem_used": info.cgroup_mem_usage(cid),
            }

        return usages

    def calc_cpu_usage(self, f, l):
        sys_diff = (l['cpu_sys'] != f['cpu_sys'])
        cgroup_diff = (l['cpu_cgroup'] != f['cpu_cgroup'])

        if sys_diff and cgroup_diff:
            core = info.cpu_cores()
            cpu_total = l['cpu_sys'] - f['cpu_sys']
            cgroup_total = l['cpu_cgroup'] - f['cpu_cgroup']
            return cgroup_total * core / cpu_total * 100 / float(10000000)
        return None

    def get_usage_rate(self):
        rates = dict()
        for cid in self.container_ids:
            first = self.first_usage[cid]
            last = self.last_usage[cid]

            cpu_rate = self.calc_cpu_usage(first, last)
            if cpu_rate:
                self.first_usage[cid] = self.last_usage[cid]
                rates[cid[0:12]] = {
                    'ports': info.container_ports(cid),
                    'cpu_used': round(cpu_rate, 3),
                    'mem_used': round(last['mem_used'], 3),
                    'mem_total': round(last['mem_total'], 3),
                    'mem_free': round(last['mem_total'] - last['mem_used'], 3)
                }
        return rates

    def live_container(self, rates):
        short_ids = [long_id[0:12] for long_id in self.container_ids]
        unlive_ids = list(set(rates.keys()) - set(short_ids))
        for container_id in unlive_ids:
            try:
                del rates[container_id]
            except KeyError:
                pass

    def get_rates(self, callback_rates):
        self.container_ids = info.container_ids()
        if len(self.container_ids) > 0:
            usages = self._get_usages()

            if len(set(self.first_usage.keys()) ^ set(usages.keys())) != 0:
                self.first_usage = usages
            else:
                self.last_usage = usages
                rates = self.get_usage_rate()
                if rates:
                    callback_rates.update(rates)
                    self.live_container(callback_rates)
                    self.callback(callback_rates, "container_status")
