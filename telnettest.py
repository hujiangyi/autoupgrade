#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from utils.SshVty import *
import os
class Linux(SshVty) :
    def __init__(self):
        SshVty.__init__(self,self)
        host = '172.17.2.150'
        port = 22
        userName = 'admin'
        password = 'admin'
        enablePassword = 'suma'
        logPath = './log/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '/'
        os.makedirs(logPath)
        self.setArg(host,0,userName,password,enablePassword,port)
        try :
            self.doConnect()
            self.send('enable')
            self.readuntil('Enable Password:',timeout=30)
            self.send(self.enablePassword)
            self.readuntil('#',timeout=30)
        except BaseException:
            msg = 'SSH login error,checkout Enable Password[{}]'.format(self.enablePassword)
            self.log(msg)
            self.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception(msg)
        self.send("show run")
        re = self.readuntil("#")
        print re
    def log(self,msg):
        print msg
    def cmdLog(self,msg):
        print msg


linux = Linux()