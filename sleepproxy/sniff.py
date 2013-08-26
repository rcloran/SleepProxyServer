from select import select
from threading import Event, Thread

from scapy.config import conf
from scapy.data import ETH_P_ALL, MTU

class SnifferThread(Thread):
    """A thread which runs a scapy sniff, and can be stopped"""

    def __init__(self, prn, filterexp, iface):
        Thread.__init__(self)
        self._prn = prn
        self._filterexp = filterexp
        self._iface = iface
        self._stop_recd = Event()

    def run(self):
        self._sniff()

    def stop(self):
        self._stop_recd.set()

    def _sniff(self):
        sock = conf.L2listen(type=ETH_P_ALL, filter=self._filterexp, iface=self._iface)

        while 1:
            try:
                sel = select([sock], [], [], 1)
                if sock in sel[0]:
                    p = sock.recv(MTU)
                    if p is None:
                        break
                    self._prn(p)
                    if self._stop_recd.is_set():
                        print "Breaking out of sniffer thread %s" % (self, )
                        break
            except KeyboardInterrupt:
                break
        sock.close()
