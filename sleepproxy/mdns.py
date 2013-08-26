import avahi
import dbus

_HOSTS = {}

def register_service(record):
    group = _get_group()

    group.AddService(
        record.get('iface', avahi.IF_UNSPEC),
        record.get('protocol', avahi.PROTO_UNSPEC),
        dbus.UInt32(record.get('flags', 0)),
        record.get('name'),
        record.get('stype'),
        record.get('domain'),
        record.get('host'),
        dbus.UInt16(record.get('port')),
        avahi.string_array_to_txt_array(record.get('text', '')),
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
                avahi.IF_UNSPEC,  # TODO
                avahi.PROTO_UNSPEC,  # TODO
                dbus.UInt32(0),  # TODO?
                str(rrset.name),
                dbus.UInt16(record.rdclass),
                dbus.UInt16(record.rdtype),
                dbus.UInt32(rrset.ttl),
                avahi.string_array_to_txt_array([record.to_digestable()])[0],
            )

def _get_group():
    """Create a group, on the system bus"""
    bus = dbus.SystemBus()
    server = dbus.Interface(
        bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
        avahi.DBUS_INTERFACE_SERVER,
    )

    return dbus.Interface(
        bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
        avahi.DBUS_INTERFACE_ENTRY_GROUP,
    )
