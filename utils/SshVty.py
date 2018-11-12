from threading import *
from paramiko import *
import time
import datetime
import traceback

MAXSSHBUF = 16 * 1024
class SshVty:
    #################################################init###############################################################
    def doConnect(self,app):
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(hostname=self.host,port=self.port,username=self.userName,password=self.password)
            self.session = self.client.get_transport().open_session()
            self.session.get_pty()
            self.session.invoke_shell()
            self.app = app
        except BaseException:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())

    def setArg(self, host, isAAA, userName, password, enablePassword):
        self.host = host
        self.isAAA = isAAA
        self.userName = userName
        self.password = password
        self.enablePassword = enablePassword
        self.log(self.host + ' ' + self.isAAA + '' + self.userName + '' + self.password + '' + self.enablePassword)

    def reconnect(self):
        self.close()
        self.log('reconnect telnet')
        self.doConnect()
        self.send('')
        self.sleepT(3)
        self.readuntil('#')
        self.log('reconnect telnet end')

    def close(self):
        try:
            self.log('close telnet ')
            self.client.close()
        except Exception, msg:
            self.app.log('traceback.format_exc():\n%s' % traceback.format_exc())
            raise Exception(msg)

    def send(self, cmd):
        self.sleepT(1)
        cmd = str('{}\r'.format(cmd))
        self.log("send cmd{}".format(cmd))
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
                    self.app.cmdLog(str)
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
                    self.app.cmdLog(str)
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
                    self.app.cmdLog(str)
                    for waitstr in waitstrs:
                        if waitstr in tmp:
                            return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            state,str = self.read()
            if not state :
                raise Exception("read ssh channel error!")
            if str is not None:
                tmp += str
                if '--More--' in str:
                    self.sendII(' ')
                self.app.cmdLog(str)
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
                    self.app.cmdLog(str)
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
                    self.app.cmdLog(str)
                    if waitstr in tmp:
                        return tmp
                else :
                    self.sleepT(1)

    def sleepT(self, delay):
        time.sleep(delay)