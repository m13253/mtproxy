#!/usr/bin/env python

import subprocess, os, pickle, threading, sys, collections

class TCacheControl:
    def __init__(self, location='/tmp/mtproxy', size=5242880, item=256):
        self.lock=threading.Lock()
        self.location=location
        self.maxSize=size
        self.size=0
        self.maxItem=item
        self.cacheList=collections.OrderedDict()
        if os.path.exists(location):
            self.LoadCache()
        else:
            self.NewCache()
        sys.stderr.write("Cache ready at %s with maxium size %d bytes or %d items.\n" % (location, size, item))
    def NewCache(self):
        subprocess.check_call(['mkdir', '-pv', self.location])
        self.SaveCache()
    def LoadCache(self):
        self.lock.acquire()
        hFile=open(os.path.join(self.location, 'mtproxy.dat'), 'rb')
        self.cacheList=pickle.load(hFile)
        hFile.close()
        self.lock.release()
    def SaveCache(self):
        self.lock.acquire()
        hFile=open(os.path.join(self.location, 'mtproxy.dat'), 'wb')
        pickle.dump(self.cacheList, hFile)
        hFile.close()
        self.lock.release()
    def WriteCache(self, index, chunk, value, size):
        self.PopItem()
        self.lock.acquire()
        if not index in self.cacheList:
            self.cacheList[index]=[]
        if chunk in self.cacheList[index]:
            self.size+=size-self.cacheList[index][chunk][1]
        else:
            self.size+=size
        self.cacheList[index][chunk]=[value, size]
        self.lock.release()
        self.SaveCache()
    def ReadCache(self, index, chunk):
        return self.cacheList[index][chunk][0]
    def PopItem(self):
        self.lock.acquire()
        while self.size>self.maxSize or len(self.cacheList)>self.maxItem:
            self.cacheList.popitem(True)
        self.lock.release()

CacheControl=TCacheControl()

# vim: et ft=python sts=4 sw=4 ts=4
