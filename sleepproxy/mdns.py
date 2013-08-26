import dbus

IF_UNSPEC = -1

PROTO_UNSPEC = -1
PROTO_INET = 0

_HOSTS = {}

def string_to_byte_array(s):
    r = []
    for c in s:
        r.append(dbus.Byte(ord(c)))
    return r

def string_array_to_txt_array(t):
    l = []
    for s in t:
        l.append(string_to_byte_array(s))
    return l

def register_service(record):
    group = _get_group()

    group.AddService(
        record.get('iface', IF_UNSPEC),
        record.get('protocol', PROTO_UNSPEC),
        dbus.UInt32(record.get('flags', 0)),
        record.get('name'),
        record.get('stype'),
        record.get('domain'),
        record.get('host'),
        dbus.UInt16(record.get('port')),
        string_array_to_txt_array(record.get('text', '')),
    )

    group.Commit()

def handle(mac, records):
    if mac in _HOSTS:
        print "I already seem to be handling mDNS for %s" % (mac, )
        return
    group = _get_group()
    _HOSTS[mac] = group
    _update_to_group(group, records)
    result = group.Commit()
    print "Result of Commit() on mDNS records was %s" % (result, )

def forget(mac):
    print "Pretending to forget %s in mDNS handler" % (mac, )
    if mac not in _HOSTS:
        print "I don't seem to be managing mDNS for %s" % (mac, )
        return

    group = _HOSTS.pop(mac)
    group.Free()

def _update_to_group(group, rrsets):
    """Convert a DNS UPDATE to additions to an mDNS group"""
    for rrset in rrsets:
        for record in rrset:
            group.AddRecord(
                IF_UNSPEC,  # TODO
                PROTO_UNSPEC,  # TODO
                dbus.UInt32(0),  # TODO?
                str(rrset.name),
                dbus.UInt16(record.rdclass),
                dbus.UInt16(record.rdtype),
                dbus.UInt32(rrset.ttl),
                string_array_to_txt_array([record.to_digestable()])[0],
            )

def _get_group():
    """Create a group, on the system bus"""
    bus = dbus.SystemBus()
    server = dbus.Interface(
        bus.get_object('org.freedesktop.Avahi', '/'),
        'org.freedesktop.Avahi.Server',
    )

    return dbus.Interface(
        bus.get_object('org.freedesktop.Avahi', server.EntryGroupNew()),
        'org.freedesktop.Avahi.EntryGroup',
    )
