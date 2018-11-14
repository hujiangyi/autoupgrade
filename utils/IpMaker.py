#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import *
from IPy import *

class IpMaker:
    def __init__(self,ipMakerType,segmentIp,segmentMask,segmentGateway,segmentExcludeIpList,iplist,cmIpMask,cmIpGateway):
        self.ipMakerType = ipMakerType
        self.ipsIndex = 0
        self.ipsIndexLock = Lock()
        if self.isSegment():
            try :
                self.segmentIpList =  IP(segmentIp + '/' + segmentMask)
                self.segmentMask = segmentMask
                self.segmentGateway = segmentGateway
            except BaseException:
                raise Exception('指定IP段配置错误，需要检查Excel中segmentIp和segmentMask列[{},{}]'.format(segmentIp,segmentMask))
            self.segmentExcludeIpList = []
            if segmentExcludeIpList == None or segmentExcludeIpList == '':
                raise Exception('指定IP段配置错误，需要检查Excel中segmentExcludeIpList列')
            else :
                ips = segmentExcludeIpList.split(',').strip()
                for ip in ips :
                    try:
                        IP(ip)
                        self.segmentExcludeIpList.append(ip)
                    except BaseException:
                        raise Exception('指定IP段配置错误，需要检查Excel中segmentExcludeIpList列[{}]'.format(ip))
        elif self.isIPList():
            if iplist == None or iplist == '':
                raise Exception('IP LIST模式配置错误，需要检查Excel中IP LIST模式列')
            else:
                ips = iplist.split(',')
                self.specifyIpList = []
                for ipFull in ips:
                    if ipFull != None and ipFull.strip() != '' :
                        parts = ipFull.split('/')
                        if len(parts) != 3:
                            raise Exception('IP LIST模式配置错误，需要检查Excel中IP LIST模式列[{}]'.format(ipFull))
                        else:
                            try :
                                specifyIp = {
                                    'ip' : IP(parts[0]).strCompressed(),
                                    'gateway' : IP(parts[1]).strCompressed(),
                                    'mask' : '255.255.255.255'
                                }
                                self.specifyIpList.append(specifyIp)
                            except BaseException:
                                raise Exception( 'IP LIST模式配置错误，需要检查Excel中IP LIST模式列[{}]'.format(ipFull))
        elif self.isCMIP():
            if cmIpGateway == None or cmIpGateway == '' or cmIpMask == None or cmIpMask == '':
                raise Exception("踢CM模式配置错误，需要检查Excel中Mask和GateWay列")
            else:
                try :
                    self.cmIpMask = IP(cmIpMask).strCompressed()
                    self.cmIpGateway = IP(cmIpGateway).strCompressed()
                    self.cmIpList = None
                except BaseException:
                    raise Exception( '踢CM模式配置错误，需要检查Mask和GateWay模式列[{},{}]'.format(cmIpMask,cmIpGateway))
        else:
            raise Exception('Excel 中 IP Masker Type字段填写错误，只能填写（Segment,IPList,CMIP）中的一个')

    def nextIp(self):
        self.ipsIndexLock.acquire()
        try:
            if self.isSegment():
                while self.ipsIndex < len(self.segmentIpList) :
                    try :
                        ip = self.segmentIpList[self.ipsIndex].strCompressed()
                        if ip not in self.segmentExcludeIpList:
                            return ip,self.segmentMask,self.segmentGateway
                    finally:
                        self.ipsIndex = self.ipsIndex + 1
                raise Exception('指定IP段配置错误，IP被用完无法分配新的IP')
            elif self.isIPList():
                if self.ipsIndex < len(self.specifyIpList) :
                    try :
                        ip = self.specifyIpList[self.ipsIndex]
                        return ip['ip'],self['mask'],self['gateway']
                    finally:
                        self.ipsIndex = self.ipsIndex + 1
                else :
                    raise Exception('IP LIST模式配置错误，IP被用完无法分配新的IP')
            elif self.isCMIP():
                if self.cmIpList == None or len(self.cmIpList) == 0:
                    raise Exception('踢CM模式配置错误，CM IP List没有被设置或没有读取到任何CM IP')
                if self.ipsIndex < len(self.cmIpList) :
                    try :
                        ip = self.cmIpList[self.ipsIndex]
                        return ip,self.cmIpMask,self.cmIpGateway
                    finally:
                        self.ipsIndex = self.ipsIndex + 1
                else :
                    raise Exception('踢CM模式配置错误，IP被用完无法分配新的IP')
        finally:
            self.ipsIndexLock.release()
    def setCmIpList(self,cmIpList):
        if isinstance(cmIpList,list):
            raise Exception('踢CM模式配置错误，CM IP LIST设置错误，必须是数组')
        self.cmIpList = cmIpList

    def isSegment(self):
        return self.ipMakerType == 'Segment'
    def isIPList(self):
        return self.ipMakerType == 'IPList'
    def isCMIP(self):
        return self.ipMakerType == 'CMIP'

