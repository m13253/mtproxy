#!/usr/bin/env python

import errno
import socket
import sys
import threading
import main
import config
import handler


class MTServer():

    def __init__(self, listen_addr, connhandler):
        self.listen_addr = listen_addr
        self.connhandler = connhandler
        self.sock = None

    def start(self):
        self.sock = socket.socket()
        while self.listen_addr[1] < 65536:
            try:
                self.sock.bind(self.listen_addr)
                break
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    self.listen_addr = (self.listen_addr[0], self.listen_addr[1] + 1)
                else:
                    raise e
        self.sock.listen(0)
        sys.stderr.write('MTProxy started on %s:%d.\n' % self.listen_addr)
        try:
            while True:
                client = self.sock.accept()
                client[0].settimeout(config.timeout)
                thehandler = self.connhandler(client[0], client[1])
                thehandler.start()
        except KeyboardInterrupt:
            pass

# vim: et ft=python sts=4 sw=4 ts=4
