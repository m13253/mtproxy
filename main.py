#!/usr/bin/env python

import socket, threading, sys
import handler

def start_server(host='localhost', port=8080, supportIPv6=False, timeout=60,
        handler=handler.ConnectionHandler):
    if supportIPv6:
        socketType=socket.AF_INET6
    else:
        socketType=socket.AF_INET
    hSocket=socket.socket(socketType)
    hSocket.bind((host, port))
    sys.stderr.write("Service started on %s:%d.\n" % (host, port))
    hSocket.listen(0)
    while True:
        socaddr=hSocket.accept()
        handler(socaddr[0], socaddr[1], timeout).run()

# vim:ts=4 sts=4 et syntax=python
