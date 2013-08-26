# ad-hoc tests for the UDP server

from sleepproxy.udp import DatagramServer


def echo(*args, **kwargs):
    print args
    print kwargs
    # print "Message from %s: %s" % (message, address)

if __name__ == '__main__':
    server = DatagramServer(('127.0.0.1', 6000), echo)
    print "Starting UDP server on port 6000..."
    server.serve_forever()
