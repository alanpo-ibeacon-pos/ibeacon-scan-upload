# test BLE Scanning software
# jcs 6/8/2014

import sys

import blescan
import bluetooth._bluetooth as bluez
import bt_g_util
import tracesReporting as report

trace = False
attend = False
useMySql = False

if len(sys.argv) <= 1:
    print("args: [--attend] [--trace [--mysql]]")

for argn in sys.argv:
    if not argn.startswith('--'):
        continue

    argn = argn[2:]

    if argn == 'attend':
        attend = True
    elif argn == 'mysql':
        useMySql = True
    elif argn == 'trace':
        trace = True

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

while True:
    returnedList = blescan.parse_events(sock, 1)
    print("----------")
    for beacon in returnedList:
#        print(str(beacon.txpower) + ", " + str(beacon.rssi));
        print(beacon)
        if attend:
            print(report.in_http_attend(cBdaddr, beacon).content)
        if trace:
            if useMySql:
                report.in_mysql(cBdaddr, beacon)
            else:
                print(report.in_http(cBdaddr, beacon).status_code)
