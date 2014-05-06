#!/usr/bin/python

# Installation:
# sudo pip install python-daemon

import argparse
import hombit
import os
import sys
import lockfile
import signal

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rpi", action="store_true")
parser.add_argument("-d", "--daemon", action="store_true")
parser.add_argument("-p", "--pidfile")
parser.add_argument("-D", "--debug", action="store_true")
arguments = parser.parse_args()

if arguments.rpi:
    from hombit.raspberrypi import RaspberryPi
    device = RaspberryPi()
else:
    from hombit.simulator import Simulator
    device = Simulator()

if __name__ == "__main__":
    if arguments.daemon:
        import daemon

        daemon_context = daemon.DaemonContext(working_directory="/tmp", uid=os.getuid())
        daemon_context.signal_map = {signal.SIGTERM: hombit.api.terminate}
        if arguments.pidfile:
            daemon_context.pidfile = lockfile.FileLock(arguments.pidfile)
            hombit.api.pidfile = arguments.pidfile
        if arguments.debug:
            daemon_context.stdout = sys.stdout
            daemon_context.stderr = sys.stderr
        with daemon_context:
            hombit.api.serve(device, daemon=True)
    else:
        hombit.api.serve(device)
