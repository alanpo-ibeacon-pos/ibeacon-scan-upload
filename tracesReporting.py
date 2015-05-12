import requests
import MySQLdb

httpReportUrl = "http://itd-moodle.ddns.net/2014fyp_ips/beacons/report.php"
httpAttendUrl = "http://itd-moodle.ddns.net/2014fyp_ips/beacons/attend.php"
httpReportLocalUrl = "http://127.0.0.1/beacons/report.php"
httpUsePost = True

mysqlHost = "hkgsherlock.no-ip.org"
mysqlPort = 3306
mysqlUser = "ibeacon"
mysqlPass = "1Beac0n"
mysqlDb = "ibeacon_traces"
mysqlTable = "traces"


__mysqlPrepared = False

def in_http(devBdaddr, bleScanResult):
    return __in_http(devBdaddr, bleScanResult, httpReportUrl)

def in_http_attend(devBdaddr, bleScanResult):
    result = __in_http(devBdaddr, bleScanResult, httpAttendUrl)
    if (result.status_code == 500):
        print(result.content)
    return result

def in_http_local(devBdaddr, bleScanResult):
    return __in_http(devBdaddr, bleScanResult, httpReportLocalUrl)

def __in_http(devBdaddr, bleScanResult, url):
    beaconContent = {"selfMac": devBdaddr,
                     "uuid": bleScanResult.uuid,
                     "major": bleScanResult.major,
                     "minor": bleScanResult.minor,
                     "mac": bleScanResult.mac,
                     "txpower": bleScanResult.txpower,
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
    result = None
    try:
        result = requests.request(method, url, data=data, params=params, timeout=1.0)
    except:
        print('cannot send result http request')
    return result

def in_mysql(devBdaddr, bleScanResult):
    db = MySQLdb.connect(host=mysqlHost, port=mysqlPort, user=mysqlUser, passwd=mysqlPass, db=mysqlDb)
    cursor = db.cursor()
    sql = "INSERT INTO " + mysqlTable + "(selfMac, uuid, major, minor, mac, txpower, rssi) \
           VALUES (%d, 0x%s, %d, %d, %d, %d, %d)" % \
                                        (int(devBdaddr.replace(":", ""), 16),
                                         bleScanResult.uuid,  # .replace("-", "")
                                         bleScanResult.major,
                                         bleScanResult.minor,
                                         int(bleScanResult.mac.replace(":", ""), 16),
                                         bleScanResult.txpower,
                                         bleScanResult.rssi)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(sql)
        print(e)
        db.rollback()
    finally:
        db.close()
