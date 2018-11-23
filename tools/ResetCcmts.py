#encoding:utf-8
import traceback
import time

from UpgradeOlt import *
from ResetCcmtsDol import ResetCcmtsDol


class ResetCcmts(UpgradeOlt):
    def run(self):
        self.initLog(self.logPath,self.host)
        self.session2 = ResetCcmtsDol()
        self.session2.connect(self,self.host, self.isAAA, self.userName, self.password, self.enablePassword,self.gateway,self.slot,self.port,self.device,self.logPath,self.mac,isSsh=self.isSsh)
        self.session2.run()
        self.doConnect()
        self.doConfig()
        self.close()
    def initLog(self,logPath,host):
        key = '{}_{}_{}'.format(self.slot,self.port,self.device)
        self.logPath = logPath
        self.cmdResultFile = open("{}{}_{}CmdResult1.log".format(logPath,host,key), "w")
        self.logResultFile = open("{}{}_{}logFile1.log".format(logPath,host,key), "w")
    def doConfig(self):
        try:
            self.state,self.msg = self.doConfigCcmts(self.gateway,self.slot,self.port,self.device)
        except BaseException, msg:
            self.state, self.msg = False,msg
            self.parent.log('traceback.format_exc():\n%s' % traceback.format_exc())

    def connect(self,parent,host,isAAA,userName,password,enablePassword,gateway,slot,port,device,logPath,mac,isSsh=False):
        print 'connect to host ' + host
        self.parent = parent
        self.gateway = gateway
        self.slot = slot
        self.port = port
        self.device = device
        self.mac = mac
        self.setArg(isSsh,host,isAAA,userName,password,enablePassword)
        self.logPath = logPath

    def getResetResult(self):
        return self.state,self.msg

    def doConfigCcmts(self,gateway,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.parent.log('configCcmts {}'.format(key),cmts=key)
        self.send('end')
        self.readuntil('#')
        ip = '{}.{}.{}.{}'.format(gateway,slot,port,device)
        re = self.ping(ip)
        while not re :
            self.parent.log('ping {} error'.format(ip))
            re = self.ping(ip)
        self.parent.log('ping {} success'.format(ip))
        self.parent.log('do telnet {}'.format(ip))
        self.send('telnet {}'.format(ip))
        re = self.readuntilMutl(['Username:','username:','%Telnet exit successful','%Error:Connect to {} timeout!'.format(ip),'%Connect to {} timeout!'.format(ip)])
        if '%Telnet exit successful' in re:
            self.parent.log('%Telnet exit successful',cmts=key)
            return False,'%Telnet exit successful'
        elif '%Connect to {} timeout!'.format(ip) in re or '%Error:Connect to {} timeout!'.format(ip) in re:
            self.parent.log('%Connect to {} timeout!'.format(ip),cmts=key)
            return False,'%Connect to {} timeout!'.format(ip)
        self.send('admin')
        self.send('admin')
        self.send('enable')
        self.readuntilII('#')
        self.send('show ccmts verbose')
        self.readuntil('#')
        return self.resetCcmts(slot,port,device)

    def resetCcmts(self,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('super')
        self.readuntilII('Password:')
        self.send('8ik,(OL>')
        self.readuntil('(config-super)#')
        self.send('shell')
        self.readuntil('#')
        self.send("echo '0' > /proc/top_misc/wdt3219_mask")
        self.readuntil('#')
        time.sleep(0.1)
        self.send("cat /proc/top_misc/wdt3219_mask")
        self.readuntil('#')
        state,re = self.session2.doReset3219()
        if state :
            self.log('reset3219 success.{}'.format(re))
        else :
            self.log('reset3219 faild.{}'.format(re))
        self.session2.doExit()
        self.send('reboot')
        self.readuntil('#')
        return True, ''

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

