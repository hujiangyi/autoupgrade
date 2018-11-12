from threading import *
from IPy import *
from pyping import *
import time
import datetime
import os
import traceback
from utils.TelnetVty import TelnetVty
from utils.SshVty import SshVty

class UpgradeOlt(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.step = 1
    def doStep(self,step,func,args=None):
        if self.step < step :
            if args != None:
                func(*args)
            else :
                func()
            self.step = step
    def setRetryThreadR(self,retryThread):
        self.retryThread = retryThread
    def addRetry(self,args,step=None):
        arg = {}
        arg['args'] = args
        arg['step'] = step
        self.retryThread.retryList.append(arg)

    #################################################init###############################################################
    def setAppPath(self, appPath):
        self.appPath = appPath

    def initCmIpArg(self, cmip, mask, cmgateway):
        self.cmip = cmip
        self.mask = mask
        self.cmgateway = cmgateway
        if self.cmip == None or self.cmip == '':
            self.useNetRange = False
        else:
            self.useNetRange = True
            self.ips = IP(self.cmip + '/' + self.mask)
            self.ipsIndex = 10
            self.ipsIndexLock = Lock()

    def nextIp(self):
        self.ipsIndexLock.acquire()
        try:
            self.ipsIndex = self.ipsIndex + 1
            return self.ips[self.ipsIndex].strCompressed()
        finally:
            self.ipsIndexLock.release()

    def initLog(self, logPath, host):
        self.logPath = logPath
        self.cmdResultFile = open(logPath + host + "CmdResult.log", "w")
        self.logResultFile = open(logPath + host + "logFile.log", "w")

    def initListView(self, listView):
        self.listView = listView

    def initExcel(self, sheetW, excelRow):
        self.sheetW = sheetW
        self.excelRow = excelRow

    #################################################init###############################################################
    def doConnect(self):
        self.client.doConnect()

    def reconnect(self):
        self.client.reconnect()


    def setArg(self, host, isAAA, userName, password, enablePassword):
        self.host = host
        self.isAAA = isAAA
        self.userName = userName
        self.password = password
        self.enablePassword = enablePassword
        self.client = TelnetVty(self)
        self.client.setArg(host,isAAA,userName,password,enablePassword)

    def close(self):
        self.client.close()

    def send(self, cmd):
        self.client.send(cmd)

    def sendII(self, cmd):
        self.client.sendII(cmd)

    def readuntil(self, waitstr='xxx', timeout=0):
        return self.client.readuntil(waitstr=waitstr,timeout=timeout)

    def readuntilMutl(self, waitstrs=['xxx'], timeout=0):
        return self.client.readuntilMutl(waitstrs=waitstrs,timeout=timeout)

    def readuntilII(self, waitstr='xxx', timeout=0):
        return self.client.readuntilII(waitstr=waitstr,timeout=timeout)

    def sleepT(self, delay):
        time.sleep(delay)

    def getMainBoardTypes(self):
        return ['mpu', 'mpub', 'meu', 'mef', 'mgu']

    def checkCmd(self,cmds,errorMessage='%'):
        for cmd in cmds:
            self.send(cmd)
            re = self.readuntil('#')
            if errorMessage not in re :
                return cmd,re
        return None,re

    def cmdExists(self,checkCmd,default):
        runCmd = 'list | include ' + checkCmd
        self.send(runCmd)
        listresult = self.readuntil('#')
        lss = listresult.split('\r\n')
        cmd = default
        for s in lss:
            if runCmd in s:
                continue
            if checkCmd in s:
                cmd = checkCmd
        return cmd

    def cmdLog(self, str):
        self.cmdResultFile.write(str)
        self.cmdResultFile.flush()

    def log(self, str,cmts=None,headName='result'):
        print self.host,str
        str = datetime.datetime.now().strftime('%Y%m%d%H%M%S\t') + str + '\n'
        self.logResultFile.write(str)
        self.logResultFile.flush()
        if cmts == None:
            self.listView.setData(self.host,headName,str)
        else :
            self.listView.setData(self.host + "_" + cmts,headName,str)

    def writeResult(self, msg,cmts=None):
        if cmts == None:
            self.listView.setData(self.host,'result',msg)
        else :
            self.listView.setData(self.host + "_" + cmts,'result',msg)
        self.sheetW.write(self.excelRow, 5, msg)

    ###############################################download#############################################################
    def downloadImage(self):
        return False
    def allBoard(self):
        self.log('get all board')
        self.send('show board | include IS')
        re = self.readuntil('#')
        bs = re.split('\r\n')
        bArray = []
        for s in bs :
            if 'show board' in s:
                continue
            if 'Filtering...' in s:
                continue
            if '#' in s:
                continue
            if s == '':
                continue
            cols = s.split()
            if len(cols) == 5 and cols[4] == 'IS':
                bArray.append(cols)
        return bArray
    def rebootOlt(self):
        self.log('rebootOlt start ')
        self.send('end')
        self.readuntil('#')
        bArray = self.allBoard()
        self.log('online board count(' + `len(bArray)` + ')')
        self.send('system reboot ')
        re = self.readuntilMutl(['System will reboot! Continue?(y/n) [n]','#'])
        self.send('y')
        self.readuntil('System now is rebooting,please wait.')
        self.close()
        time.sleep(180)
        while True:
            r = ping(self.host)
            if r.ret_code == 0 :
                break
        time.sleep(180)
        self.doConnect()
        self.send('')
        self.readuntil('#')
        while True:
            nbArray = self.allBoard()
            self.log('new online board count(' + `len(nbArray)` + ')')
            if len(bArray) == len(nbArray) :
                compare = True
                for i in range(0,len(nbArray)):
                    b = bArray[i]
                    nb = nbArray[i]
                    for j in range(0,len(nb)):
                        bCol = b[j]
                        nbCol = nb[j]
                        if bCol != nbCol :
                            self.log('compare False:' + `bArray` + ' ' + `nbArray`)
                            compare = False
                            break
                    else :
                        continue
                    break
                if compare :
                    break
                else:
                    time.sleep(10)
            else:
                time.sleep(10)
        self.log('rebootOlt success ')

    def flashType(self):
        flashType = 0  # only tffs0 = 0 ;include tffs0 and yaffs2 = 1
        self.send('end')
        self.readuntil('#')
        self.send('cd /')
        self.readuntil('#')
        self.send('ls')
        lsInfo = self.readuntil('#')
        lis = lsInfo.split('\r\n')
        for s in lis:
            if 'yaffs2' in s:
                flashType = 1
        return flashType


    def freeSize(self,path):
        self.send('cd ' + path)
        pwdStr = self.readuntil('#')
        self.send('ls')
        lsInfo = self.readuntil('#')
        lis = lsInfo.split('\r\n')
        for s in lis:
            if 'Free size' in s:
                indexStart = s.index(':')
                indexEnd = s.index('bytes')
                ts = s[indexStart + 1:indexEnd].strip()
                return int(ts)

    def imageTypeAndFreeSize(self):
        self.log('imageTypeAndFreeSize')
        flashType = self.flashType()
        if flashType == 0 :
            tffs0FreeSize = self.freeSize('/tffs0')
            return flashType,tffs0FreeSize,0
        elif flashType == 1:
            tffs0FreeSize = self.freeSize('/tffs0')
            yaffs2FreeSize = self.freeSize('/yaffs2')
            return flashType,tffs0FreeSize,yaffs2FreeSize
        else:
            raise Exception("unkown image type")

    def imageFileSizeOnOlt(self,isActiveAndStandby,mainFile,otherFiles):
        self.log('imageFileSizeOnOlt')
        fileSizes = {}
        self.send('end')
        self.readuntil('#')
        cmds = ['show image-info all','show all file-info']
        if isActiveAndStandby :
            cmds = ['show image-info master all','show master all file-info']
        cmd,lsInfo = self.checkCmd(cmds)
        lis = lsInfo.split('\r\n')
        for s in lis:
            if cmd in s:
                continue
            elif 'Main mpu' in s:
                continue
            elif 'File Name' in s:
                continue
            elif '---' in s:
                continue
            elif 'Total size:' in s:
                continue
            elif '#' in s:
                continue
            cols = s.split()
            for f in otherFiles:
                if f in s and 'appbak' not in s:
                    fileSizes[f] = int(cols[3])
                    break
        return fileSizes

    def imageFileSize(self,mainFile,otherFiles):
        fileSizes = {}
        if not self.appPath.endswith('/'):
            self.appPath += '/'
        for f in otherFiles:
            try:
                fFileSize = os.path.getsize(self.appPath + f + '.bin')
                fileSizes[f] = int(fFileSize)
            except Exception, msg:
                self.log(`msg`)
        return fileSizes

    def checkFreeSize(self,isActiveAndStandby,mainFile,otherFiles):
        self.log('checkFreeSize')
        imageType,tffs0FreeSize,yaffs2FreeSize = self.imageTypeAndFreeSize()
        self.log('imageTypeAndFreeSize:' + `imageType` + '\t' + `tffs0FreeSize` + '\t' + `yaffs2FreeSize`)
        fileSizesOnOlt = self.imageFileSizeOnOlt(isActiveAndStandby,mainFile,otherFiles)
        self.log('imageFileSizeOnOlt:' + `fileSizesOnOlt`)
        fileSizes = self.imageFileSize(mainFile,otherFiles)
        self.log('imageFileSize:' + `fileSizes`)
        if imageType == 0:
            freeSize = 0
            freeSize +=  tffs0FreeSize
            for f in otherFiles:
                if fileSizesOnOlt.has_key(f):
                    freeSize +=  fileSizesOnOlt[f]
            needSize = 0
            for f in otherFiles:
                if fileSizes.has_key(f):
                    needSize += fileSizes[f]
            if needSize >= freeSize:
                raise Exception("checkFreeSize error")
        elif imageType == 1:
            freeSize = 0
            freeSize +=  yaffs2FreeSize
            for f in otherFiles:
                if fileSizesOnOlt.has_key(f):
                    freeSize +=  fileSizesOnOlt[f]
            needSize = 0
            for f in otherFiles:
                if fileSizes.has_key(f):
                    needSize += fileSizes[f]
            if needSize >= freeSize:
                raise Exception("checkFreeSize error")

    def getSysObjectId(self):
        self.send('end')
        self.readuntil('#')
        self.send('show system')
        systemInfo = self.readuntil(waitstr='#')
        si = systemInfo.split('\r\n')
        sysObjectId = ''
        for s in si:
            if 'System total service slots' in s:
                indexStart = s.index(':')
                indexEnd = len(s)
                if indexStart == -1:
                    raise Exception('Read olt type error')
                ts = s[indexStart + 1:indexEnd].strip()
                totalSlot = int(ts)
                # self.log('totalSlot:' + str(totalSlot))
                if totalSlot == 3:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2'
                elif totalSlot == 8:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.3'
                elif totalSlot == 18:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.1'
                else:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2.x'
        return sysObjectId

    def allImageTypeAndFileName(self):
        self.send('end')
        self.readuntil('#')
        sysObjectId = self.getSysObjectId()
        self.send('show board')
        boardInfo = self.readuntil(waitstr='#')
        # self.log(boardInfo)
        self.send('configure terminal')
        self.readuntil('(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs:
            if 'show board' in s:
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s:
                continue
            if '------' in s:
                continue
            if 'Total:' in s:
                continue
            if '#' in s:
                continue
            slotid = s[2:4].strip()
            assignType = s[9:13].strip()
            presentType = s[26:33].strip()
            adminStatus = s[43:46]
            operationStatus = s[60:64]
            # self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
            if '*' in slotid:
                #self.log('slotid:' + slotid)
                if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1':
                    #8601
                    if assignType == 'mpub':
                        return True,'mpub',['epu','geu','gpu','xgu','bootrom','bootrom-e500','bootrom_mpub']
                    else:
                        return True,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.2':
                    #8602
                    return False,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3':
                    #8603
                    if assignType == 'mpub':
                        return True,'mpub',['epu','geu','gpu','xgu','bootrom','bootrom-e500','bootrom_mpub']
                    else:
                        return True,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                else:
                    if 'meu' in assignType or 'mefa' in assignType or 'mefb' in assignType:
                        return False,'meu',['bootrom-e500']
                    elif 'mef' in assignType:
                        return False,'mef',['bootrom']
                    else:
                        return False,'mgu',['bootrom-e500']
    #################################################syncFile###########################################################
    def syncFile(self):
        self.sleepT(3)
        cmd = self.cmdExists('show file-sync-status','show file sync-status')
        self.log('sync config file')
        self.send('sync config file')
        re = self.readuntilMutl(['Are you sure?(y/n) [n]','#'])
        if '%' not in re :
            self.send('y')
            self.readuntil('#')
            self.send(cmd)
            tmp = self.read()
            while 'successfully' not in tmp:
                self.sleepT(10)
                self.send(cmd)
                tmp += self.read()
            self.sleepT(3)
            tmp += self.read()
            self.log('sync app file')
            self.send('sync app file')
            self.readuntil('Are you sure?(y/n) [n]')
            self.send('y')
            self.readuntil('#')
            self.send(cmd)
            tmp = self.read()
            while 'successfully' not in tmp:
                self.sleepT(10)
                self.send(cmd)
                tmp += self.read()
            self.sleepT(3)
            tmp += self.read()
            self.writeResult('syncFile success')
        else:
            self.log('syncFile error:' + re)
            self.writeResult('syncFile error' + re)

    ###################################################upgrade##########################################################
    def upgradeAllBootrom(self):
        self.log('upgradeAllBootrom')
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if '*' in slotid:
                    slotid = slotid[0:1]
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('upgradeAllBootrom success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    def upgradeMpubBootrom(self):
        self.log('upgradeMpubBootrom')
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if 'mpu' not in assignType:
                    continue
                else :
                    if '*' in slotid:
                        slotid = slotid[0:1]
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('upgradeMpubBootrom success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    def upgradeServiceBootrom(self):
        self.log('upgradeServiceBootrom')
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if 'mpu' in assignType:
                    continue
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('upgradeServiceBootrom success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    #####################################################collectData####################################################
    def collectData(self,type):
        cmdfilepath = './collectDataCmd.txt'
        if not os.path.exists(cmdfilepath):
            return
        cmdfile = open(cmdfilepath, "r")
        fo = open(self.logPath + self.host + type + 'Upgrade.txt', "w")
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        for line in cmdfile.readlines():
            line = line.strip()
            self.log('{}'.format(line))
            self.send('{}'.format(line))
            tmp = self.readuntil('(config)#')
            fo.write(tmp + '\n')
            fo.write('split------------------------------------------\n')
            fo.flush()
        fo.close()
        cmdfile.close()

    def isGpon(self,slotType):
        return 'gpu' in slotType

    def ping(self, ip):
        self.send('ping {} -c 1'.format(ip))
        re = self.readuntil('#')
        if ' 0% packet loss' in re:
            return True
        else:
            return False