#!/usr/bin/env python

import pdb

import socket, threading, select, sys, re
import config

class ConnectionHandler(threading.Thread):
    def __init__(self, client_sock, client_addr):
        threading.Thread.__init__(self)
        self.client=[client_sock, client_addr, b'']
        self.server=[None, None, b'']

    def run(self):
        try:
            method, path, version=self.parsehead(self.client)
            sys.stderr.write('%s:%d: %s %s\n' % (self.client[1][0], self.client[1][1], method, path))
            params=self.parseparam(self.client)
            if self.client[0]:
                self.client[0].close()
        except socket.error:
            self.senderr(503, 'Service Unvailable')
        except KeyboardInterrupt:
            self.senderr(503, 'Service Unvailable')

    def recv(self, peer):
        if peer[0]:
            try:
                peer[2]+=peer[0].recv(config.buffer_length)
            except socket.error as e:
                if e.errno not in {socket.EAGAIN, socket.EWOULDBLOCK}:
                    raise e

    def parsehead(self, peer):
        while peer[0]:
            idx=peer[2].find(b'\n')
            if idx==-1:
                self.recv(peer)
            else:
                headline, peer[2]=peer[2].split(b'\n', 1)
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

    def parseparam(self, peer):
        params={}
        while peer[0]:
            while peer[0]:
                idx=peer[2].find(b'\n')
                if idx==-1:
                    self.recv(peer)
                else:
                    rline, peer[2]=peer[2].split(b'\n', 1)
                    break
            line=rline.rstrip(b'\r').decode('utf-8', 'replace')
            if line=='':
                break
            values=line.split(': ', 1)
            if len(values)>1:
                params[values[0]]=values[1]
            else:
                peer[2]=rline+peer[2]
                break
        return params

    def senderr(self, number, desc, httpver='HTTP/1.1'):
        try:
            if self.server[0]:
                if self.server[2]:
                    try:
                        self.server[0].sendall(self.server[2])
                        self.server[2]=b''
                    except socket.error:
                        pass
                self.server[0].close()
                self.server[0]=None
        except socket.error:
            pass
        try:
            if self.client[0]:
                try:
                    self.client[0].sendall(('%s %s %s\r\nConnection: close\r\n\r\n' % (httpver, number, desc)).encode('utf-8', 'replace'))
                except socket.error:
                    pass
                self.client[2]=b''
                self.client[0].close()
                self.client[0]=None
        except socket.error:
            pass

# vim: et ft=python sts=4 sw=4 ts=4
