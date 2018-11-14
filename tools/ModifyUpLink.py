# -*- coding: utf-8 -*-
import traceback
import time
from ConfigCcmtsUplink import ConfigCcmtsUplink
from UpgradeCcmts import UpgradeCcmts


class ModifyUpLink(UpgradeCcmts):
    def run(self):
        row={"identifyKey":"ip",
             "ip":self.host,
             "result":"start",
             "isAAA":self.isAAA == '1',
             "userName":self.userName,
             "password":self.password,
             "enablePassword":self.enablePassword}
        self.listView.insertRow(row)
        self.doTelnet()
        self.doConfig()
    def doConfig(self):
        try:
            state = self.configUplink(self.vlan,self.gateway,self.ftpServer,self.ftpUserName,self.ftpPassword,self.configFile)
            if state:
                self.writeResult('cmts count[' + `len(self.allkey)` + '] success[' + `self.successCount` + '] faild[' + `self.faildCount` + ']' )
            else :
                self.writeResult('no cmts upgraded')
        except BaseException, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def connect(self,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,excelRow,vlan,gateway,ftpServer,ftpUserName,ftpPassword,configFile,threadNum,ccFilter,listView):
        print 'connect to host ' + host
        self.listView = listView
        self.vlan = vlan
        self.gateway = gateway
        self.ftpServer = ftpServer
        self.ftpUserName = ftpUserName
        self.ftpPassword = ftpPassword
        self.configFile = configFile
        self.threadNum = threadNum
        self.ccFilter = ccFilter
        self.initCmIpArg(cmip,mask,cmgateway)
        self.initListView(listView)
        self.initExcel(sheetW,excelRow)
        self.initLog(logPath,host)
        self.setTelnetArg(host,isAAA,userName,password,enablePassword)

    def configUplink(self,vlan,gateway,ftpServer,ftpUsername,ftpPassword,configFile):
        self.log('configUplink')
        self.allCmts,self.allkey,self.allVersion,self.allMac = self.getAllOnlineCmts(raiseException=True)
        self.successCount = 0
        self.faildCount = 0
        configThreads = []
        filterMap = self.makeFilterMap(self.ccFilter)
        for slot,portMap in self.allCmts.items():
            for port,deviceList in portMap.items():
                slotVlan = int(vlan)
                slotGateway = int(gateway)
                state,msg = self.doConfigPon(slotVlan,0,slot,port,'epu',slotGateway)
                for device in deviceList:
                    key = '{}/{}/{}'.format(slot,port,device)
                    if '*' not in filterMap:
                        if not filterMap.has_key(slot):
                            self.log('continue cmts {}'.format(key))
                            continue
                        else :
                            slotMap = filterMap.get(slot)
                            if '*' not in slotMap :
                                if not slotMap.has_key(port):
                                    self.log('continue cmts {}'.format(key))
                                    continue
                                else :
                                    portMap = slotMap.get(port)
                                    if '*' not in portMap:
                                        if not portMap.has_key(device):
                                            self.log('continue cmts {}'.format(key))
                                            continue
                    while True:
                        for t in configThreads:
                            if not t.isAlive():
                                state,msg = t.getConfigResult()
                                if not state :
                                    self.log(msg)
                                    #self.writeResult(msg)
                                    self.faildCount = self.faildCount + 1
                                else :
                                    self.successCount = self.successCount + 1
                                configThreads.remove(t)
                                break
                        if len(configThreads) < self.threadNum :
                            configCcmtsUplink = ConfigCcmtsUplink()
                            configCcmtsUplink.connect(self,self.host, self.isAAA, self.userName, self.password, self.enablePassword, self.cmip, self.mask,
                                                 self.cmgateway, vlan, gateway,
                                                 ftpServer,ftpUsername,ftpPassword,configFile,slot,port,device)
                            configCcmtsUplink.setDaemon(True)
                            configCcmtsUplink.start()
                            configThreads.append(configCcmtsUplink)
                            break
                        else :
                            time.sleep(10)

        while True:
            if len(configThreads) == 0:
                break
            removeThread = []
            for t in configThreads:
                if not t.isAlive():
                    state, msg = t.getConfigResult()
                    if not state:
                        self.log(msg)
                        # self.writeResult(msg)
                        self.faildCount = self.faildCount + 1
                    else:
                        self.successCount = self.successCount + 1
                    removeThread.append(t)
                    break
            for t in removeThread:
                configThreads.remove(t)
        return True

    def makeFilterMap(self,ccFilter):
        re = {}
        if ccFilter == None or ccFilter.strip() == '' :
            return re
        keys = ccFilter.split(',')
        for key in keys:
            cols = key.split('/')
            if len(cols) == 3 :
                slot = cols[0]
                port = cols[1]
                device = cols[2]
                slotMap = {}
                if re.has_key(slot) :
                    slotMap = re.get(slot)
                else :
                    re[slot] = slotMap
                portMap = {}
                if slotMap.has_key(port):
                    portMap = slotMap.get(port)
                else :
                    slotMap[port] = portMap
                if not portMap.has_key(device) :
                    portMap[device] = ''
        return re

