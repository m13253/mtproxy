#!/usr/bin/env python

import pdb

import socket, threading, select, os, sys
import config

class ConnectionHandler(threading.Thread):
    def __init__(self, client_addr):
        threading.Thread.__init__(self)
        self.client=client
        self.client_buffer=''
        self.server=None
        self.address=address
        self.timeout=timeout

    def run(self):
        self.method, self.path, self.protocol=self.get_base_header()
        if self.method=='GET':
            self.method_GET()
        elif self.method=='CONNECT':
            self.method_CONNECT()
        else:
            self.method_others()
        self.client.close()
        if self.server:
            self.server.close()

    def get_base_header(self):
        while True:
            self.client_buffer+=self.client.recv(ver.BUFLEN).decode()
            end=self.client_buffer.find('\n')
            if end!=-1:
                break
        sys.stderr.write('%s\n' % self.client_buffer[:end])
        data=(self.client_buffer[:end+1]).split()
        self.client_buffer=self.client_buffer[end+1:]
        return data

    def method_GET(self):
        self.method_others()

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(("%s 200 Connection established\nX-Proxy-agent: %s\n\n" % (ver.HTTPVER, ver.VERSION)).encode())
        self.client_buffer=''
        self._read_write()

    def method_others(self):
        self.path=self.path[7:]
        i=self.path.find('/')
        if i!=-1:
            host=self.path[:i]
            path=self.path[i:]
        else:
            host=self.path
            path='/'
        self._connect_target(host)
        self.server.send(('%s %s %s\n%s' % (self.method, path, self.protocol, self.client_buffer)).encode())
        self.client_buffer=''
        self._read_write()

    def _connect_target(self, host):
        i=host.find(':')
        if i!=-1:
            port=int(host[i+1:])
            host=host[:i]
        else:
            port=80
        (soc_family, _, _, _, address)=socket.getaddrinfo(host, port)[0]
        self.server=socket.socket(soc_family)
        self.server.connect(address)

    def _read_write(self):
        time_out_max=self.timeout/3
#        pdb.set_trace()
        socs=[self.client, self.server]
        count=0
        while True:
            count+=1
            (recv, _, error)=select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for soc_in in recv:
                    data=soc_in.recv(ver.BUFLEN)
                    if soc_in is self.client.fileno():
                        soc_out=self.server
                    else:
                        out=self.client
                    if data:
                        out.send(data)
                        count=0
            if count==time_out_max:
                break

# vim: et ft=python sts=4 sw=4 ts=4
