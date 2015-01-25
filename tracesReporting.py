import requests
import MySQLdb

httpUrl = "http://hkgsherlock.no-ip.org/beacons/report.php"
httpUsePost = True

mysqlHost = "hkgsherlock.no-ip.org"
mysqlPort = 3306
mysqlUser = "ibeacon"
mysqlPass = "1Beac0n"
mysqlDb = "ibeacon-traces"
mysqlTable = "traces"


__mysqlPrepared = False

def in_http(devBdaddr, bleScanResult):
    beaconContent = {"selfMac": devBdaddr,
                     "uuid": bleScanResult.uuid,
                     "major": bleScanResult.major,
                     "minor": bleScanResult.minor,
                     "mac": bleScanResult.mac,
                     "txpower": bleScanResult.u_txpower,
                     "rssi": bleScanResult.rssi}
    method = ''
    data = None
    params = None
    if httpUsePost:
        method = 'post'
        data = beaconContent
    else:
        method = 'get'
        params = beaconContent
    r = requests.request(method, httpUrl, data=data, params=params)
    # return r.status_code == 200 & r.content == "1"


def in_mysql(devBdaddr, bleScanResult):
    db = MySQLdb.connect(mysqlHost + ":" + str(mysqlPort), mysqlUser, mysqlPass, mysqlDb)
    cursor = db.cursor()
    sql = "INSERT INTO " + mysqlTable + "(selfMac, uuid, major, minor, mac, txpower, rssi) \
           VALUES (%x, 0x%s, %d, %d, %x, %d, %d)" % \
                                        (devBdaddr.replace(":", ""),
                                         bleScanResult.uuid,  # .replace("-", "")
                                         bleScanResult.major,
                                         bleScanResult.minor,
                                         bleScanResult.mac.replace(":", ""),
                                         bleScanResult.u_txpower,
                                         bleScanResult.rssi)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()