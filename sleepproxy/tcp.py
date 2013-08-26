from functools import partial

from scapy.all import IP, TCP

import sleepproxy.manager
from sleepproxy.sniff import SnifferThread
from sleepproxy.wol import wake

_HOSTS = {}

def handle(mac, addresses, iface):
    print "Pretending to handle incoming SYN for %s: %s" % (mac, addresses, )

    if mac in _HOSTS:
        print "Ignoring already managed host %s" % (mac, )

    for address in addresses:
        if ':' in address:
            # TODO: Handle IP6
            continue
        print 'Starting TCP sniffer for %s' % (address, )
        thread = SnifferThread(
            filterexp="tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack = 0 and dst host %s" % (address, ),
            prn=partial(_handle_packet, mac, address),
            iface=iface,
        )
        _HOSTS[mac] = thread
        thread.start()

def forget(mac):
    print "Pretending to forget host %s in TCP handler" % (mac, )
    if mac not in _HOSTS:
        print "I don't seem to know about %s, ignoring" % (mac, )
        return
    _HOSTS[mac].stop()
    del _HOSTS[mac]

def _handle_packet(mac, address, packet):
    """Do something with a SYN for the other machine!"""
    if not (IP in packet and TCP in packet):
        return
    if packet[IP].dst != address:
        print "Sniffed a TCP SYN for the wrong address!?"
        print packet.show()
        return
    wake(mac)

    # TODO: Check if it awoke?
    sleepproxy.manager.forget_host(mac)
