import sleepproxy.mdns as mdns
import sleepproxy.arp as arp
import sleepproxy.tcp as tcp

def manage_host(info):
    mdns.handle(info['othermac'], info['records'])
    arp.handle(info['othermac'], info['addresses'], info['mymac'], info['myif'])
    tcp.handle(info['othermac'], info['addresses'], info['myif'])

def forget_host(mac):
    mdns.forget(mac)
    arp.forget(mac)
    tcp.forget(mac)
