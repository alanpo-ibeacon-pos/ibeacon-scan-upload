def calDistance(txPower, rssi):
    if rssi == 0:
        return 0.0
    ratio = rssi*1.0/txPower
    if ratio < 1.0:
        return ratio**10
    else:
        accuracy = 0.89976*(ratio**7.7095) + 0.111
        return accuracy