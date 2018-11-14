#encoding:gbk
import traceback
import time
import datetime

from UpgradeOlt import *

class ResetCcmtsDol(UpgradeOlt):
    def run(self):
        self.initLog(self.logPath,self.host)
        self.doConnect()
        # self.doConfig()
    def initLog(self,logPath,host):
        key = '{}_{}_{}'.format(self.slot,self.port,self.device)
        self.logPath = logPath
        self.cmdResultFile = open("{}{}_{}CmdResult2.log".format(logPath,host,key), "w")
        self.logResultFile = open("{}{}_{}logFile2.log".format(logPath,host,key), "w")
    def doReset3219(self):
        try:
            return self.reset3219(self.gateway,self.slot,self.port,self.device)
        except BaseException, msg:
            self.parent.log('traceback.format_exc():\n%s' % traceback.format_exc())
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            return False,`msg`

    def connect(self,parent,host,isAAA,userName,password,enablePassword,gateway,slot,port,device,logPath,mac):
        print 'connect to host ' + host
        self.parent = parent
        self.gateway = gateway
        self.slot = slot
        self.port = port
        self.device = device
        self.mac = mac
        self.setArg(host,isAAA,userName,password,enablePassword)
        self.logPath = logPath

    def getResetResult(self):
        return self.state,self.msg

    def reset3219(self,gateway,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.parent.log('configCcmts {}'.format(key),cmts=key)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('super')
        self.readuntilII('Password:')
        self.send(self.sp())
        re = self.readuntilMutl(['(config-super)#','(config)#'])
        if '%Bad password.' in re:
            self.parent.log('%Enter super model error(Bad password)',cmts=key)
            return False,'%Enter super model error(Bad password)'
        self.send('test')
        self.readuntil('(config-super-test)#')
        self.send('ccmts-cmd {} shell reboot'.format(self.mac))
        re = self.readuntil('(config-super-test)#')
        if 'ccmts-cmd  failed!' in re:
            return False,'ccmts-cmd  failed!'
        else :
            return True,re

    def doExit(self):
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('>')
        self.send('exit')
        self.close()
    def cmdLog(self, str):
        self.parent.cmdLog(str)
        try:
            self.cmdResultFile.write(str)
            self.cmdResultFile.flush()
        except BaseException, msg:
            print msg

    def log(self, str,cmts=None,headName='result'):
        self.parent.log(str,cmts,headName)
        try:
            str = '{} {}\n'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S\t'), str )
            self.logResultFile.write(str)
            self.logResultFile.flush()
        except BaseException, msg:
            print msg
    def writeResult(self, msg,cmts=None):
        self.parent.writeResult(msg,cmts)
    def sp(self):
        i = datetime.datetime.now()
        year = i.year * 17
        month = (i.month + 12) * 19
        day = i.day +23
        pwd = year * 1000 + month * 100 + day * (day + 29) * 341 -7
        return str(pwd)
