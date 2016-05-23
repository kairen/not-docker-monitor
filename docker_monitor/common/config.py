# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

from ConfigParser import SafeConfigParser

DEFAULT_CONF_PATH = "/etc/docker-monitor/docker-monitor.conf"


class Configuration:
    """
    Parsing system conf args
    """

    PROFILE_KEYS = [
        "role", "host", "port", "queue",
        "username", "password", "timeout",
    ]

    def __init__(self, conf_path):
        self.conf_path = conf_path if conf_path is not None else DEFAULT_CONF_PATH
        print(self.conf_path)
        self.parser = SafeConfigParser()
        self.parser.read(self.conf_path)

    def debug(self):
        return self.parser.getboolean("default", "debug")

    def window_time(self):
        return self.parser.getfloat("default", "window_time")

    def rabbit_profile(self):
        profiles = {
            key: self.parser.get(
                "rabbit_messaging",
                key
            ) for key in self.PROFILE_KEYS
        }
        return profiles
