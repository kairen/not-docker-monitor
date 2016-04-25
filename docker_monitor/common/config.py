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
