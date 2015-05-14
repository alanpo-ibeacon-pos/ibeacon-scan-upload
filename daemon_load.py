#!/usr/bin/env python

import sys, time
from daemon import Daemon
import main

class BleScannerDaemon(Daemon):
    args = []

    def run(self):
        main.entrypoint().main(self.args)

if __name__ == "__main__":
    daemon = BleScannerDaemon('/var/run/ibeacon-scan-upload.pid', '/dev/null', sys.stdout.name, sys.stderr.name)
    daemon.args = sys.argv[2:]
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print('daemonised version of the beacon tracer')
        print("usage: %s start|stop|restart %s" % (sys.argv[0], main.strUsage))
        sys.exit(2)
