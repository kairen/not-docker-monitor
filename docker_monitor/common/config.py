# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

from ConfigParser import SafeConfigParser


class Configuration:
    """
    Parsing system conf args
    """

    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.parser = SafeConfigParser()
        self.parser.read(self.conf_path)

    def debug(self):
        return self.parser.getboolean("default", "debug")

    def window_time(self):
        return self.parser.getfloat("default", "window_time")

    def rabbit_role(self):
        return self.parser.get(
            "rabbit_messaging",
            "role"
        )

    def rabbit_host(self):
        return self.parser.get(
            "rabbit_messaging",
            "host"
        )

    def rabbit_port(self):
        return self.parser.getint(
            "rabbit_messaging",
            "port"
        )

    def rabbit_queue(self):
        return self.parser.get(
            "rabbit_messaging",
            "queue"
        )

    def rabbit_user(self):
        return self.parser.get(
            "rabbit_messaging",
            "username"
        )

    def rabbit_passwd(self):
        return self.parser.get(
            "rabbit_messaging",
            "password"
        )

    def rabbit_timeout(self):
        return self.parser.getint(
            "rabbit_messaging",
            "connect_timeout"
        )
