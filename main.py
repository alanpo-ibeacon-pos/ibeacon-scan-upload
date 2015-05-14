# test BLE Scanning software
# jcs 6/8/2014

import sys
import threading

import blescan
import bluetooth._bluetooth as bluez
import bt_g_util
import tracesReporting as report

strUsage = "[--httpjson] | [--trace [--mysql]] [--tracelocal [--sqlite]]"

class entrypoint:
    def __init__(self):
        self.toBeSent = []
        self.lock = threading.Lock()

    def main(self, args):
        httpjson = False
        trace = False
        useMySql = False
        traceToLocal = False
        useSqlite = False

        if len(args) == 0:
            print('user-mode beacon tracer and reporter')
            print('usage: %s %s' % (sys.argv[0], strUsage))

        for argn in args:
            if not argn.startswith('--'):
                continue

            argn = argn[2:]

            if argn == 'httpjson':
                httpjson = True
            elif argn == 'mysql':
                useMySql = True
            elif argn == 'trace':
                trace = True
            elif argn == 'tracelocal':
                traceToLocal = True
            elif argn == 'sqlite':
                useSqlite = True

        dev_id = 0
        # dev_id = hci_devid( "01:23:45:67:89:AB" );
        try:
            sock = bluez.hci_open_dev(dev_id)
            print("ble thread started")
        except:
            print("error accessing bluetooth device...")
            sys.exit(1)

        cBdaddr = bt_g_util.read_local_bdaddr(sock)
        print(cBdaddr)
        blescan.hci_le_set_scan_parameters(sock)
        blescan.hci_enable_le_scan(sock)

        if httpjson:
            threading.Timer(interval=2.0, target=self.SendBatchAndClearTray).start()

        while True:
            returnedList = blescan.parse_events(sock, 1)

            for e in returnedList:
                e.selfMac = cBdaddr

            if httpjson:
                self.lock.acquire()
                self.toBeSent += returnedList
                self.lock.release()
            else:
                for beacon in returnedList:
                    print('scanned beacon with pairing: u=%s, M=%d, m=%d. sig: [%d/%d]' % (beacon.uuid, beacon.major, beacon.minor, beacon.rssi, beacon.txpower))
                    if trace:
                        if useMySql:
                            threading.Thread(target=report.in_mysql, args=[beacon]).start()
                        else:
                            threading.Thread(target=report.in_http, args=[beacon]).start()

                    if traceToLocal:
                        if useSqlite:
                            threading.Thread(target=report.in_sqlite, args=[beacon]).start()
                        else:
                            threading.Thread(target=report.in_http_local, args=[beacon]).start()

    def SendBatchAndClearTray(self):
        threading.Timer(interval=2.0, target=self.SendBatchAndClearTray).start()
        self.lock.acquire()
        sending = self.toBeSent
        self.toBeSent = []
        self.lock.release()
        report.in_http_list_as_json(sending)



if __name__ == "__main__":
    entrypoint().main(sys.argv[1:])