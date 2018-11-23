#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import *
from paramiko import *
import time
import datetime
import traceback

MAXSSHBUF = 16 * 1024
class SshVty:
    def __init__(self,app):
        self.app = app
    #################################################init###############################################################
    def doConnect(self):
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(hostname=self.host,port=self.port,username=self.userName,password=self.password)
            self.session = self.client.get_transport().open_session()
            self.session.get_pty()
            self.session.invoke_shell()
        except BaseException:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("doConnect error")

    def setArg(self, host, isAAA, userName, password, enablePassword,port=22):
        self.host = host
        self.isAAA = isAAA
        self.userName = userName
        self.password = password
        self.enablePassword = enablePassword
        self.port = port
        self.app.log('{} {} {} {} {} {}'.format(self.host,self.isAAA,self.userName,self.password,self.enablePassword,self.port))

    def reconnect(self):
        self.close()
        self.app.log('reconnect telnet')
        self.doConnect()
        self.send('')
        self.sleepT(3)
        self.readuntil('#')
        self.app.log('reconnect telnet end')

    def close(self):
        try:
            self.app.log('close telnet ')
            self.client.close()
        except Exception, msg:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception(msg)

    def send(self, cmd):
        self.sleepT(1)
        cmd = str('{}\r'.format(cmd))
        try:
            self.session.send(cmd)
        except Exception:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("ssh write error!")

    def sendII(self, cmd):
        cmd = str(cmd)
        try:
            self.session.send(cmd)
        except Exception:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("ssh write error!")

    def read(self, delay=1):
        while True:
            outReady = self.session.recv_ready()
            errorReady = self.session.recv_stderr_ready()
            if outReady :
                out = self.session.recv(MAXSSHBUF)
                self.app.cmdLog(out)
                return True,out
            if errorReady :
                error = self.session.recv_stderr(MAXSSHBUF)
                self.app.cmdLog(error)
                return False,error

    def readuntil(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    time.sleep(1)
                    if '--More--' in str:
                        self.sendII(' ')
                    if waitstr in tmp:
                        return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    if '--More--' in str:
                        self.sendII(' ')
                    if waitstr in tmp:
                        return tmp
                else :
                    self.sleepT(1)

    def readuntilMutl(self, waitstrs=['xxx'], timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    time.sleep(1)
                    if '--More--' in str:
                        self.sendII(' ')
                    for waitstr in waitstrs:
                        if waitstr in tmp:
                            return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    if '--More--' in str:
                        self.sendII(' ')
                    for waitstr in waitstrs:
                        if waitstr in tmp:
                            return tmp
                else :
                    self.sleepT(1)

    def readuntilII(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    time.sleep(1)
                    if '--More--' in str:
                        self.sendII(' ')
                    if waitstr in tmp:
                        return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                state,str = self.read()
                if not state :
                    raise Exception("read ssh channel error!")
                if str is not None:
                    tmp += str
                    if '--More--' in str:
                        self.sendII(' ')
                    if waitstr in tmp:
                        return tmp
                else :
                    self.sleepT(1)

    def sleepT(self, delay):
        time.sleep(delay)