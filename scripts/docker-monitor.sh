#!/bin/sh
### BEGIN INIT INFO
# Provides:          docker-monitor
# Required-Start:    $network $local_fs $remote_fs $syslog
# Required-Stop:     $remote_fs
# Should-Start:      postgresql mysql ntp
# Should-Stop:       postgresql mysql ntp
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Docker Monitor
# Description:       Collect docker cgroup usage
### END INIT INFO

# Author: Kyle Bai <kyle.b@inwinstack.com>

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="docker"
PROJECT_NAME="docker"
NAME=${PROJECT_NAME}-monitor
DAEMON=/usr/local/bin/${NAME}
DAEMON_ARGS="--options args"
PIDFILE=/var/run/${NAME}/${NAME}.pid
SCRIPTNAME=/etc/init.d/${NAME}-service
SYSTEM_USER=${NAME}
SYSTEM_GROUP=${NAME}
STARTDAEMON_CHUID="--chuid ${SYSTEM_USER}:${SYSTEM_GROUP}"

# Read configuration variable file if it is present
[ -r /etc/default/${NAME} ] && . /etc/default/${NAME}

. /lib/lsb/init-functions

#
# Function that starts the daemon/service
#
do_start() {
    if ls /var/run/${NAME} | grep -Fxq "${NAME}.pid"
    then
        log_daemon_msg "Already Starting $DESC" "${NAME} service ..."
    else
        log_daemon_msg "Starting $DESC" "${NAME} service ..."
        start-stop-daemon --start --quiet --background --make-pidfile --pidfile $PIDFILE --exec $DAEMON > /dev/null \
        || return 1
    fi
}

#
# Function that stops the daemon/service
#
do_stop() {
        start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE --name $NAME
        RETVAL="$?"
        [ "$RETVAL" = 2 ] && return 2

        start-stop-daemon --stop --quiet --oknodo --retry=0/30/KILL/5 --exec $DAEMON
        [ "$?" = 2 ] && return 2
        # Many daemons don't delete their pidfiles when they exit.
        rm -f $PIDFILE
        return "$RETVAL"
}

#
# Function run debug to the daemon/service
#
do_debug() {
        start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON > /dev/null \
        || return 1
}

case "$1" in
  start)
        do_start
        case "$?" in
                0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
                2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
        esac
        ;;
  stop)
        log_daemon_msg "Stopping $DESC" "${NAME} service ..."
        do_stop
        case "$?" in
                0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
                2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
        esac
        ;;
  systemd-start)
        do_debug
        case "$?" in
                0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
                2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
        esac
        ;;
  restart)
        log_daemon_msg "Restarting $DESC" "${NAME} service ..."
        do_stop
        case "$?" in
          0|1)
                do_start
                case "$?" in
                        0) log_end_msg 0 ;;
                        1) log_end_msg 1 ;; # Old process is still running
                        *) log_end_msg 1 ;; # Failed to start
                esac
                ;;
          *)
                # Failed to stop
                log_end_msg 1
                ;;
        esac
        ;;
  *)
        echo "Usage: $SCRIPTNAME {start|stop|restart|systemd-start}" >&2
        exit 3
        ;;
esac

: