import struct

import dns.message
import dns.reversename
import IPy
import netifaces

from sleepproxy.manager import manage_host

def handle(server, raddress, message):
    try:
        message = dns.message.from_wire(message)
    except:
        print "Error decoding DNS message"
        return

    if message.edns < 0:
        print "Received non-EDNS message, ignoring"
        return

    if not (message.opcode() == 5 and message.authority):
        print "Received non-UPDATE message, ignoring"
        return

    info = {'records': [], 'addresses': []}

    # Try to guess the interface this came in on
    for iface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(iface)
        for af, addresses in ifaddresses.items():
            if af != 2:  # AF_INET
                continue
            for address in addresses:
                net = IPy.IP(address['addr']).make_net(address['netmask'])
                if IPy.IP(raddress[0]) in net:
                    info['mymac'] = ifaddresses[17][0]['addr']
                    info['myif'] = iface

    for rrset in message.authority:
        info['records'].append(rrset)
        _add_addresses(info, rrset)

    for option in message.options:
        if option.otype == 2:
            info['ttl'] = struct.unpack("!L", option.data)
        if option.otype == 4:
            info['othermac'] = option.data.encode('hex_codec')[4:]

    # TODO: endsflags seems to indicate some other TTL

    # TODO: Better composability
    manage_host(info)

    _answer(server.socket, raddress, message)

def _add_addresses(info, rrset):
    # Not sure if this is the correct way to detect addresses.
    if rrset.rdtype != dns.rdatatype.PTR or rrset.rdclass != dns.rdataclass.IN:
        return

    # Meh.
    if not rrset.name.to_text().endswith('.arpa.'):
        return

    info['addresses'].append(dns.reversename.to_address(rrset.name))

def _answer(sock, address, query):
    response = dns.message.make_response(query)
    sock.sendto(response.to_wire(), address)

