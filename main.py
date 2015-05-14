# test BLE Scanning software
# jcs 6/8/2014

import sys
import threading

import blescan
import bluetooth._bluetooth as bluez
import bt_g_util
import tracesReporting as report

strUsage = "[--httpjson] [--httpjsonlocal] | [--trace [--mysql]] [--tracelocal [--sqlite]]"

class entrypoint:
    def __init__(self):
        self.toBeSent = []
        self.lock = threading.Lock()
        self.httpjson = False
        self.httpjsonlocal = False
        self.trace = False
        self.useMySql = False
        self.traceToLocal = False
        self.useSqlite = False

    def main(self, args):

        if len(args) == 0:
            print('user-mode beacon tracer and reporter')
            print('usage: %s %s' % (sys.argv[0], strUsage))
            sys.exit(0)

        for argn in args:
            if not argn.startswith('--'):
                continue

            argn = argn[2:]

            if argn == 'blackhole':
                self.httpjson = False
                self.httpjsonlocal = False
                self.trace = False
                self.useMySql = False
                self.traceToLocal = False
                self.useSqlite = False
                break
            else:
                if argn == 'httpjson':
                    self.httpjson = True
                elif argn == 'httpjsonlocal':
                    self.httpjsonlocal = True
                elif argn == 'mysql':

                    self.useMySql = True
                elif argn == 'trace':
                    self.trace = True
                elif argn == 'tracelocal':
                    self.traceToLocal = True
                elif argn == 'sqlite':
                    self.useSqlite = True
                else:
                    print('Not heard of argument \"%s\", exiting' % argn)
                    sys.exit(1)

        dev_id = 0
        # dev_id = hci_devid( "01:23:45:67:89:AB" );
        try:
            sock = bluez.hci_open_dev(dev_id)
            print("ble thread started")
        except:
            print("error accessing bluetooth device...")
            sys.exit(1)

        cBdaddr = bt_g_util.read_local_bdaddr(sock)
        print('using bluetooth device with mac address of:  %s' % cBdaddr)
        blescan.hci_le_set_scan_parameters(sock)
        blescan.hci_enable_le_scan(sock)

        if self.httpjson or self.httpjsonlocal:
            threading.Timer(2.0, self.SendBatchAndClearTray).start()

        while True:
            returnedList = blescan.parse_events(sock, 1)

            for e in returnedList:
                print('scanned beacon with pairing: u=%s, M=%d, m=%d. sig: [%d/%d]'
                      % (e.uuid, e.major, e.minor, e.rssi, e.txpower))
                e.selfMac = cBdaddr

            if self.httpjson or self.httpjsonlocal:
                self.lock.acquire()
                self.toBeSent += returnedList
                self.lock.release()
            else:
                for beacon in returnedList:
                    if self.trace:
                        if self.useMySql:
                            threading.Thread(target=report.in_mysql, args=[beacon]).start()
                        else:
                            threading.Thread(target=report.in_http, args=[beacon]).start()

                    if self.traceToLocal:
                        if self.useSqlite:
                            threading.Thread(target=report.in_sqlite, args=[beacon]).start()
                        else:
                            threading.Thread(target=report.in_http_local, args=[beacon]).start()

    def SendBatchAndClearTray(self):
        threading.Timer(2.0, self.SendBatchAndClearTray).start()
        self.lock.acquire()
        sending = self.toBeSent
        self.toBeSent = []
        self.lock.release()
        if len(sending) == 0:
            return
        if self.httpjson:
            report.in_http_list_as_json(sending)
        if self.httpjsonlocal:
            report.in_http_local_list_as_json(sending)


if __name__ == "__main__":
    entrypoint().main(sys.argv[1:])