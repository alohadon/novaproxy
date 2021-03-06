#!/usr/bin/python
# coding=utf-8

# Copyright (c) 2009 Alejandro R. Sedeño

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Opens a port that you can connect to for a root shell on the Pre.
# I recommend using PuTTY in raw mode with
# "Terminal> Line discipline options" all set to "Force off"

import socket, select, struct
from subprocess import Popen

MAGIC=0xdecafbad # Cute, Palm.
myport=8023

def getport():
    sock = getsocket(6968)
    line = sock.recv(1024)
    portnum = line.split(" ")[0]
    return int(portnum)

def getsocket(port):
    s = socket.socket()
    s.connect(("localhost", port))
    return s

class sock_helper:
    "Just a little something to buffer this socket."
    def __init__(self,sock):
        self.sock = sock
        self.buf = ''

    def get_bytes(self,i):
        while(len(self.buf) < i):
            self.buf += self.sock.recv(i)
        ret = self.buf[:i]
        self.buf = self.buf[i:]
        return ret

def send_str(sock, string):
    sock.send(struct.pack('<IIII',MAGIC,1,len(string),0)+string)

def recv_str(sh):
    header = sh.get_bytes(16)
    (magic, version, length, unknown) = struct.unpack('<IIII',header)
    if (magic != MAGIC):
        print "Unexpected magic value [0x%x]." % magic
        exit(-1)
    if (version != 1):
        print "Unexpected protocol version [0x%x]." % version
        exit(-1)
    if (unknown != 0):
        print "Done."
        sh.sock.close()
    return sh.get_bytes(length)

def novaterm(port):
    listener = socket.socket()
    listener.bind(('localhost',myport))
    listener.listen(1)
    print "Listening on localhost, port %i." % myport
    (insock, addr) = listener.accept()
    print "Connecting to novacom, running on port: %s" % (port)
    sock = getsocket(port)
    sh = sock_helper(sock)
    sock.send("open tty://")
    sh.get_bytes(5)

    try:
        while 1:
            (r,w,e) = select.select((sock,insock),(),())
            if (sock in r):
                insock.send(recv_str(sh))
                while(len(sh.buf) > 0):
                    insock.send(recv_str(sh))
            if (insock in r):
                send_str(sock, insock.recv(1024))
    finally:
        listener.close()
        insock.close()
        sock.close()


if __name__=="__main__":
    port = getport()
    novaterm(port)
