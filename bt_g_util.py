import bluetooth._bluetooth as bluez
import struct


def read_local_bdaddr(hci_sock):
    old_filter = hci_sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_INFO_PARAM,
                                   bluez.OCF_READ_BD_ADDR)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    hci_sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    bluez.hci_send_cmd(hci_sock, bluez.OGF_INFO_PARAM, bluez.OCF_READ_BD_ADDR)

    pkt = hci_sock.recv(255)

    status, raw_bdaddr = struct.unpack("xxxxxxB6s", pkt)
    assert status == 0

    t = ["%X" % ord(b) for b in raw_bdaddr]
    t.reverse()
    bdaddr = ":".join(t)

    # restore old filter
    hci_sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return bdaddr