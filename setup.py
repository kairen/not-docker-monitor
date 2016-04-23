# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

from setuptools import setup, find_packages
import sys

if sys.version_info <= (2, 5):
    error = "ERROR: docker-monitor requires Python Version 2.6 or above...exiting."
    print(error)
    sys.exit(1)

requirements = [
    'pika>=0.10.0',
]

setup(
    name='docker-monitor',
    version='0.1.0',
    packages=find_packages(),
    description='Collect docker meters data',
    author='Kyle Bai',
    author_email='kyle.b@inwinstack.com',
    url='https://www.gitbook.com/@kairen',
    install_requires=requirements,
    license="MIT",
    entry_points={
        'console_scripts': [
            'docker-monitor = docker_monitor.collector:main',
        ],
    },
)