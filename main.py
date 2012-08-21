#!/usr/bin/env python

import socket, threading, sys
import config, server, handler

quiting=False
threads=[]

def start_server():
    main_server=server.MTServer((config.listen_on, config.port), handler.ConnectionHandler)
    try:
        main_server.start()
    except KeyboardInterrupt:
        quiting=True

# vim: et ft=python sts=4 sw=4 ts=4
