from UpgradeOlt import UpgradeOlt

class UpgradeOltFtpServer(UpgradeOlt):
    def connect(self,host,isAAA,userName,password,enablePassword,ftpIp,ftpUserName,ftpPassword):
        print 'connect to host ' + host
        try:
            self.setArg(host,isAAA,userName,password,enablePassword)
            self.ftpIp = ftpIp
            self.ftpUserName = ftpUserName
            self.ftpPassword = ftpPassword
        except BaseException, msg:
            self.log(`msg`)
            msg = 'telnet connecting failed'
            raise Exception(msg)

    def doDownload(self,type, file):
        self.send('end')
        self.readuntil('#')
        self.send('download ' + type + ' ' + self.ftpIp + ' ' + self.ftpUserName + ' ' + self.ftpPassword + ' ' + file)
        self.log('download ' + type + ' ' + self.ftpIp + ' ' + self.ftpUserName + ' ' + self.ftpPassword + ' ' + file)
        self.readuntil('#')
        self.sleepT(10)
        cmd = self.cmdExists('show file-transfer-status','show file transfering-status')
        self.send(cmd)
        fts = self.readuntil('#')
        
        while 'successfully' not in fts:
            if 'transfer failed' in fts:
                raise Exception(file + " transfer failed")
            self.sleepT(10)
            self.send(cmd)
            fts = self.readuntil('#')

    def downloadImage(self):
        try:
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
                    self.log('slotid:' + slotid)
                    if assignType == 'mpub':
                        self.log('mpub')
                        # mpub
                        self.log('download mpub')
                        self.doDownload('mpub', 'mpub.bin')
                        self.log('download epu')
                        self.doDownload('epu', 'epu.bin')
                        self.log('download geu')
                        self.doDownload('geu', 'geu.bin')
                        self.log('download gpu')
                        self.doDownload('gpu', 'gpu.bin')
                        self.log('download xgu')
                        self.doDownload('xgu', 'xgu.bin')
                        self.log('download bootrom')
                        self.doDownload('bootrom', 'bootrom.bin')
                        self.log('download bootrom-e500')
                        self.doDownload('bootrom-e500', 'bootrom-e500.bin')
                    else:
                        self.log('mpua')
                        if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1':
                            self.log('8601')
                            # 8601
                            self.log('download mpu')
                            self.doDownload('mpu', 'mpu.bin')
                            self.log('download epu')
                            self.doDownload('epu', 'epu.bin')
                            self.log('download geu')
                            self.doDownload('geu', 'geu.bin')
                            self.log('download gpu')
                            self.doDownload('gpu', 'gpu.bin')
                            self.log('download xgu')
                            self.doDownload('xgu', 'xgu.bin')
                            self.log('download bootrom')
                            self.doDownload('bootrom', 'bootrom.bin')
                            self.log('download bootrom-e500')
                            self.doDownload('bootrom-e500', 'bootrom-e500.bin')
                        if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.2':
                            self.log('8602')
                            # 8602
                            self.log('download mpu')
                            self.doDownload('mpu', 'mpu.bin')
                            self.log('download epu')
                            self.doDownload('epu', 'epu.bin')
                            self.log('download xgu')
                            self.doDownload('xgu', 'xgu.bin')
                            self.log('download bootrom')
                            self.doDownload('bootrom', 'bootrom.bin')
                            self.log('download bootrom-e500')
                            self.doDownload('bootrom-e500', 'bootrom-e500.bin')
                        elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3':
                            self.log('8603')
                            # 8603
                            self.log('download mpu')
                            self.doDownload('mpu', 'mpu.bin')
                            self.log('download epu')
                            self.doDownload('epu', 'epu.bin')
                            self.log('download geu')
                            self.doDownload('geu', 'geu.bin')
                            self.log('download gpu')
                            self.doDownload('gpu', 'gpu.bin')
                            self.log('download xgu')
                            self.doDownload('xgu', 'xgu.bin')
                            self.log('download bootrom')
                            self.doDownload('bootrom', 'bootrom.bin')
                            self.log('download bootrom-e500')
                            self.doDownload('bootrom-e500', 'bootrom-e500.bin')
                        else:
                            self.log('other 8602e 8602ef')
                            # other 8602e 8602ef
                            self.log('download mef')
                            self.doDownload('mef', 'mef.bin')
                            self.log('download bootrom')
                            self.doDownload('bootrom', 'bootrom.bin')
            return True
        except Exception, msg:
            self.log(`msg`)
            return False
