#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import *
from telnetlib import *
import time
import datetime
import traceback

class TelnetVty:
    def __init__(self,app):
        self.app = app
    #################################################init###############################################################
    def doConnect(self):
        try:
            self.telnet = Telnet(self.host)
        except BaseException:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("doConnect error")

    def setArg(self, host, isAAA, userName, password, enablePassword,port=23):
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
            self.telnet.close()
        except Exception, msg:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception(msg)

    def send(self, cmd):
        terminator = '\r'
        cmd = str(cmd)
        cmd += terminator
        try:
            self.telnet.write(cmd)
        except Exception:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("telnet write error!")

    def sendII(self, cmd):
        cmd = str(cmd)
        try:
            self.telnet.write(cmd)
        except Exception:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception("telnet write error!")

    def read(self, delay=1):
        str = self.telnet.read_very_eager()
        self.app.cmdLog(str)
        return str

    def readuntil(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                tmp += self.read()
                time.sleep(1)
                if tmp.endswith('--More--'):
                    self.sendII(' ')
                if waitstr in tmp:
                    return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                #self.app.log(tmp)
                if self.needLogin(tmp):
                    tmp = ''
                    self.send('')
                    tmp += self.read()
                if waitstr in tmp:
                    return tmp

    def readuntilMutl(self, waitstrs=['xxx'], timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                time.sleep(1)
                tmp += self.read()
                if tmp.endswith('--More--'):
                    self.sendII(' ')
                for waitstr in waitstrs:
                    if waitstr in tmp:
                        return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                #self.app.log(tmp)
                if self.needLogin(tmp):
                    tmp = ''
                    self.send('')
                    tmp += self.read()
                for waitstr in waitstrs:
                    if waitstr in tmp:
                        return tmp

    def readuntilII(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                time.sleep(1)
                tmp += self.read()
                if waitstr in tmp:
                    return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                if waitstr in tmp:
                    return tmp

    def needLogin(self, str):
        try:
            #self.app.log('CLI timeout need login.')
            if self.isAAA:
                if 'sername:' in str :
                    self.send('')
                    re = self.readuntilII(waitstr='sername:', timeout=30)
                    self.send(self.userName)
                    self.readuntilII(waitstr='assword:', timeout=30)
                    self.send(self.password)
                    self.readuntilII('>', timeout=30)
                    self.send('en')
                    self.readuntilII('#', timeout=30)
                    return True
                else :
                    return False
            else:
                if 'assword:' in str :
                    self.send('')
                    self.readuntilII(waitstr='assword:', timeout=30)
                    self.send(self.password)
                    self.readuntilII('>', timeout=30)
                    self.send('en')
                    self.readuntilII('Enable Password:', timeout=30)
                    self.send(self.enablePassword)
                    self.readuntilII('#', timeout=30)
                    return True
                else :
                    return False
        except Exception, msg:
            self.app.log(`msg`)
            raise Exception("login faild!")

    def sleepT(self, delay):
        time.sleep(delay)
