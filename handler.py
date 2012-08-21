#!/usr/bin/env python

import pdb

import socket, threading, select, os, sys, re
import config

class ConnectionHandler(threading.Thread):
    def __init__(self, client, client_addr):
        threading.Thread.__init__(self)
        self.client=client
        self.client_addr=client_addr
        self.client_buffer=b''
        self.server=None
        self.server_buffer=b''

    def run(self):
        try:
            method, path, version=self.parsehead()
            params=self.parseparam()
            print(method, path, version, params)
            self.client.close()
        except socket.error:
            pass

    def recv(self):
        try:
            self.client_buffer+=self.client.recv(config.buffer_length)
        except socket.error as e:
            if e.errno not in {socket.EAGAIN, socket.EWOULDBLOCK}:
                raise e

    def parsehead(self):
        while True:
            idx=self.client_buffer.find(b'\n')
            if idx==-1:
                self.recv()
            else:
                headline, self.client_buffer=self.client_buffer.split(b'\n', 1)
                break
        headline=headline.rstrip(b'\r').decode('utf-8', 'replace')
        spaces=len(re.findall(' ', headline))
        if spaces==0:
            self.senderr(400, 'Bad Request')
            return None, None, None
        elif spaces==1:
            method, path=headline.split(' ', 1)
            return method, path, 'HTTP/1.0'
        else:
            method, pathver=headline.split(' ', 1)
            path=re.findall('^.*(?= )', pathver)[0]
            clientver=pathver[len(path)+1:]
            return method, path, clientver

    def parseparam(self):
        params={}
        while True:
            while True:
                idx=self.client_buffer.find(b'\n')
                if idx==-1:
                    self.recv()
                else:
                    rline, self.client_buffer=self.client_buffer.split(b'\n', 1)
                    break
            line=rline.rstrip(b'\r').decode('utf-8', 'replace')
            if line=='':
                break
            values=line.split(': ', 1)
            if len(values)>1:
                params[values[0]]=values[1]
            else:
                self.client_buffer=rline+self.client_buffer
                break
        return params

    def senderr(self, number, desc, httpver='HTTP/1.1'):
        try:
            if self.server:
                self.server.close()
                self.server=None
        except socket.error:
            pass
        try:
            if self.client:
                self.client.sendall('%s %s %s\r\nConnection: close\r\n\r\n' % (httpver, number, desc))
                self.client.close()
                self.client=None
        except socket.error:
            pass

# vim: et ft=python sts=4 sw=4 ts=4
