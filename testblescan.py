# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import requests
import bluetooth._bluetooth as bluez
import bt_g_util


dev_id = 0
# dev_id = hci_devid( "01:23:45:67:89:AB" );
try:
        sock = bluez.hci_open_dev(dev_id)
        print("ble thread started")

except:
        print("error accessing bluetooth device...")
        sys.exit(1)

print(bt_g_util.read_local_bdaddr(sock))
blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

while True:
        returnedList = blescan.parse_events(sock, 1)
        print("----------")
        for beacon in returnedList:
                print(beacon)
                # beaconContent = {"a": "a"}
                # r = requests.get("http://hkgsherlock.no-ip.org/beacons/report.php", params=beaconContent)