#encoding:utf-8
from UpgradeOlt import UpgradeOlt


class PingTest(UpgradeOlt) :
    def run(self):
        row={"identifyKey":"ip",
             "ip":self.host,
             "result":"start",
             "isAAA":self.isAAA,
             "userName":self.userName,
             "password":self.password,
             "enablePassword":self.enablePassword}
        self.listView.insertRow(row)
        self.doConnect()
        re = self.ping('50.7.4.1')
        print re

    def connect(self,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,excelRow,listView):
        print 'connect to host ' + host
        self.listView = listView
        self.initCmIpArg(cmip,mask,cmgateway)
        self.initListView(listView)
        self.initExcel(sheetW,excelRow)
        self.initLog(logPath,host)
        self.setArg(host,isAAA,userName,password,enablePassword)
