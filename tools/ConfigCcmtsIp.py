#encoding:gbk
import traceback
import time

from UpgradeOlt import *

class ConfigCcmtsIp(UpgradeOlt):
    def run(self):
        self.initLog(self.logPath,self.host)
        self.doConnect()
        self.doConfig()
        self.close()
    def initLog(self,logPath,host):
        key = '{}_{}_{}'.format(self.slot,self.port,self.device)
        self.logPath = logPath
        self.cmdResultFile = open("{}{}_{}CmdResult.log".format(logPath,host,key), "w")
        self.logResultFile = open("{}{}_{}logFile.log".format(logPath,host,key), "w")
    def doConfig(self):
        try:
            self.state,self.msg = self.doConfigCcmts(self.vlan,self.gateway,self.ftpServer,self.slot,self.port,self.device)
        except BaseException, msg:
            self.state, self.msg = False,msg
            self.parent.log('traceback.format_exc():\n%s' % traceback.format_exc())
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def connect(self,parent,host,isAAA,userName,password,enablePassword,vlan,gateway,ftpServer,slot,port,device,slotType,cmvlan,logPath,mac,ipMaker,isSsh=False):
        print 'connect to host ' + host
        self.parent = parent
        self.vlan = vlan
        self.gateway = gateway
        self.ftpServer = ftpServer
        self.slot = slot
        self.port = port
        self.device = device
        self.slotType = slotType
        self.ipMaker = ipMaker
        self.cmvlan = cmvlan
        self.mac = mac
        self.setArg(isSsh,host,isAAA,userName,password,enablePassword)
        self.logPath = logPath

    def getUpgradeResult(self):
        return self.state,self.msg



    def doConfigCcmts(self,vlan,gateway,ftpServer,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        row = {"identifyKey": "ip",
               "ip": key,
               "result": "start",
               "clearResult": "",
               "isAAA": self.isAAA == '1',
               "userName": self.userName,
               "password": self.password,
               "enablePassword": self.enablePassword}
        self.parent.listView.insertChildRow(self.host,row)
        self.parent.log('configCcmts vlan {} {}/{}/{}'.format(vlan,slot,port,device),cmts=key)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts {}'.format(key))
        self.readuntil('(config-if-ccmts-{})#'.format(key))
        self.send('onu-ipconfig ip-address {0}.{1}.{2}.{3} mask 255.0.0.0 gateway {0}.254.0.1 cvlan {4}'.format(gateway,slot,port,device,vlan))
        re = self.readuntil('(config-if-ccmts-{})#'.format(key))
        if '%This command does not support GPON CCMTS, and the corresponding GPON' in re:
            self.send('exit')
            self.readuntil('(config)#')
            self.send('interface gpon {}/{}'.format(slot,port))
            self.readuntil('(config-if-gpon-{}/{})#'.format(slot,port))
            self.send('onu-ipconfig {3} ip-index 1 static ip-address {0}.{1}.{2}.{3} mask 255.0.0.0 gateway {0}.254.0.1 vlan {4}'.format(gateway,slot,port,device,vlan))
            self.readuntil('(config-if-gpon-{}/{})#'.format(slot,port))
        time.sleep(5)
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
        cmtsIp,cmtsMask,cmtsGateway = self.ipMaker.nextIp()
        while True:
            if cmtsIp == cmtsGateway :
                cmtsIp = self.ipMaker.nextIp()
            r = self.ping(cmtsIp)
            if r :
                cmtsIp = self.ipMaker.nextIp()
                if cmtsIp == cmtsGateway:
                    cmtsIp = self.ipMaker.nextIp()
            else:
                break
        self.parent.log('cmts ip is {}'.format(cmtsIp), cmts=key)
        state,msg = self.configCmtsIp(cmtsIp,cmtsMask,cmtsGateway,ftpServer,slot,port,device)
        while not state:
            cmtsIp = self.parent.nextIp()
            if cmtsIp == cmtsGateway :
                cmtsIp = self.parent.nextIp()
            state, msg = self.configCmtsIp(cmtsIp,cmtsMask,cmtsGateway, ftpServer,slot,port,device)
        self.send('exit')
        self.readuntil('>')
        self.send('exit')
        self.send('')
        self.readuntil('#')
        return state,msg


    def configCmtsIp(self,cmtsIp,cmtsMask,cmtsGateway,ftpServer,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts 1/1/1')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('cable upstream 1-4 shutdown')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('cable downstream 1-16 shutdown')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('exit')
        self.readuntil('(config)#')
        self.send('no ip address primary')
        self.readuntil('(config)#')
        self.send('no ip address dhcp-alloc')
        self.readuntil('(config)#')
        cv = self.cmvlan
        if not self.isGpon(self.slotType) :
            if cv == 1:
                cv = 0
        if cv != 0:
            self.send('interface vlanif {}'.format(cv))
            self.readuntil('#')
            self.send('ip address {} {} primary'.format(cmtsIp,cmtsMask))
            self.readuntil('#')
            self.send('exit')
            self.readuntil('#')
        else :
            self.send('ip address {} {} primary'.format(cmtsIp,cmtsMask))
            self.readuntil('#')
        if cmtsGateway != None:
            self.send('gateway {}'.format(cmtsGateway) )
            self.readuntil('(config)#')
        self.send('super')
        self.readuntilII('Password:')
        self.send('8ik,(OL>')
        self.readuntil('(config-super)#')
        self.send('shell')
        self.readuntil('#')
        self.send('ping {}'.format(ftpServer))
        self.readuntil('#')
        self.send('echo $?')
        re = self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        lines = re.split('\r\n')
        for s in lines:
            if 'echo $?' in s:
                continue
            if '#' in s:
                continue
            if '0' == s:
                self.parent.log('{}config success!cmtsIp:{}'.format(key,cmtsIp), cmts=key)
                return True, ''
            else:
                self.parent.log('{}ftp server can not connect.cmtsIp:{}'.format(key,cmtsIp), cmts=key)
                return False, '{}ftp server can not connect.cmtsIp:{}'.format(key,cmtsIp)

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
            str = '{} {}\n'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S\t'),str)
            self.logResultFile.write(str)
            self.logResultFile.flush()
        except BaseException, msg:
            print msg
    def writeResult(self, msg,cmts=None):
        self.parent.writeResult(msg,cmts)

