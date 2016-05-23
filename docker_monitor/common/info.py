# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved


import datetime
import commands
import socket


def hostname():
    return socket.gethostname()


def ip_addr():
    return commands.getoutput(
        "ip route get 8.8.8.8 | awk '{print $NF; exit}'"
    )


def update_time():
    return str(datetime.datetime.now())


def cpu_cores():
    return int(commands.getoutput("egrep -c '(vmx|svm)' /proc/cpuinfo"))


def cpu_total():
    return int(commands.getoutput(
        "awk '/cpu / {for(i=2;i<=NF;i++) t+=$i; print t; t=0}' /proc/stat"
    ))


def cpu_idle():
    return int(commands.getoutput(
        "awk '/cpu / {print $5+$6}' /proc/stat"
    ))


def cpu_speed():
    return float(commands.getoutput(
        "awk '/cpu MHz/ {print $4}' /proc/cpuinfo"
    )) / float(1024)


def mem_total():
    return int(commands.getoutput(
        "awk '/MemTotal: / {print $2}' /proc/meminfo"
    )) / float(1024)


def mem_free():
    return int(commands.getoutput(
        "awk '/MemFree: / {print $2}' /proc/meminfo"
    )) / float(1024)


def mem_used():
    return mem_total() - mem_free()
