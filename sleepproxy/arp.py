from functools import partial

from scapy.all import ARP, Ether, sendp

from sleepproxy.sniff import SnifferThread

_HOSTS = {}

def handle(othermac, addresses, mymac, iface):
    print 'Pretending to handle arp for %s on %s' % (addresses, iface)

    if othermac in _HOSTS:
        print "I already seem to be managing %s, ignoring"
        return

    for address in addresses:
        if ':' in address:
            # TODO: Handle IP6
            continue
        thread = SnifferThread(
            filterexp="arp host %s" % (address, ),
            prn=partial(_handle_packet, address, mymac),
            iface=iface,
        )
        _HOSTS[othermac] = thread
        thread.start()

def forget(mac):
    print "Pretending to forget %s in ARP" % (mac, )
    if mac not in _HOSTS:
        print "I don't seem to be managing %s" % (mac, )
        return
    _HOSTS[mac].stop()
    del _HOSTS[mac]

def _handle_packet(address, mac, packet):
    if ARP not in packet:
        # I don't know how this happens, but I've seen it
        return
    if packet[ARP].op != ARP.who_has:
        return
    # TODO: Should probably handle is-at by deregistering!
    if packet[ARP].pdst != address:
        print "Skipping packet with pdst %s != %s" % (packet[ARP].pdst, address, )
        return

    ether = packet[Ether]
    arp = packet[ARP]

    reply = Ether(
        dst=ether.src, src=mac) / ARP(
            op="is-at",
            psrc=arp.pdst,
            pdst=arp.psrc,
            hwsrc=mac,
            hwdst=packet[ARP].hwsrc)
    print "Sending ARP response for %s" % (arp.pdst, )
    sendp(reply)
