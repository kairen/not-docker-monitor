#!/usr/bin/env python
import sys
from docker_monitor.collector import main

"""
Collect docker meters, and publish to server using RabbitMQ
"""

if __name__ == "__main__":
    sys.exit(main())
