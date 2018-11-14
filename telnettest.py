#encoding:gbk
from telnetlib import *
import time

def send(cmd):
    terminator = '\r'
    cmd = str(cmd)
    cmd += terminator
    try:
        msg = cmd
        telnet.write(cmd)
    except Exception, msg:
        raise Exception("telnet write error!")


def sendII(cmd):
    cmd = str(cmd)
    try:
        msg = cmd
        telnet.write(cmd)
    except Exception, msg:
        raise Exception("telnet write error!")


def read(delay=1):
    time.sleep(1)
    str = telnet.read_very_eager()
    return str

def readuntil(waitstr='xxx', timeout=0):
    tmp = ""
    if timeout != 0:
        delay = 0.0
        while delay <= timeout:
            tmp += read()
            if tmp.endswith('--More--'):
                sendII(' ')
            if waitstr in tmp:
                return tmp
            delay += 1
        raise Exception("wait str timeout")
    else:
        while 1:
            tmp += read()
            #log(tmp)
            if needLogin(tmp):
                tmp = ''
                send('')
                tmp += read()
            if waitstr in tmp:
                return tmp

def readuntilMutl(waitstrs=['xxx'], timeout=0):
    tmp = ""
    if timeout != 0:
        delay = 0.0
        while delay <= timeout:
            tmp += read()
            if tmp.endswith('--More--'):
                sendII(' ')
            for waitstr in waitstrs:
                if waitstr in tmp:
                    return tmp
            delay += 1
        raise Exception("wait str timeout")
    else:
        while 1:
            tmp += read()
            #log(tmp)
            if needLogin(tmp):
                tmp = ''
                send('')
                tmp += read()
            for waitstr in waitstrs:
                if waitstr in tmp:
                    return tmp

def readuntilII(waitstr='xxx', timeout=0):
    print "timeout:" + `timeout`
    tmp = ""
    if timeout != 0:
        delay = 0.0
        while delay <= timeout:
            print delay,tmp
            tmp += read()
            if waitstr in tmp:
                return tmp
            delay += 1
        raise Exception("wait str timeout")
    else:
        while 1:
            print tmp
            tmp += read()
            if waitstr in tmp:
                return tmp

def needLogin(str):
    try:
        if 'assword:' in str:
            #log('CLI timeout need login.')
            print isAAA
            if isAAA == '1':
                send('')
                re = readuntilII(waitstr='sername:', timeout=30)
                send(userName)
                print userName
                readuntilII(waitstr='assword:', timeout=30)
                send(password)
                print password
                readuntilII('>', timeout=30)
                send('en')
                readuntilII('#', timeout=30)
            else:
                print password
                send('')
                readuntilII(waitstr='assword:', timeout=30)
                send(password)
                print enablePassword
                readuntilII('>', timeout=30)
                print 1
                send('en')
                print 2
                readuntilII('Enable Password:', timeout=30)
                print 3
                send(enablePassword)
                print 4
                readuntilII('#', timeout=30)
                print 5
            return True
        else :
            return False
    except Exception, msg:
        raise Exception("login faild!")
isAAA = 0
userName = 'suma'
password = 'suma'
enablePassword = 'suma'
host = '172.17.2.150'
telnet = Telnet(host)
send('')
print readuntil('#')
send('show cable modem')
print readuntil('#')
