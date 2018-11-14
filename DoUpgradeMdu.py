#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import *
import datetime
import os
import xlrd
from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from tools.UpgradeCcmts import *
from xlutils.copy import copy
from utils.ListView import *
from utils.IpMaker import *


def selectOltExcelPath():
    path_ = askopenfilename()
    oltExcelPath.set(path_)

def rowView(row,label,textvariable,fun=None,lastLabel='no Label'):
    Label(root,text=label).grid(row=row,column=0)
    Entry(root,textvariable=textvariable).grid(row=row,column=1)
    if fun != None:
        Button(root,text='select',command=fun).grid(row=row,column=2)
    if lastLabel != 'no Label' :
        Label(root,text=lastLabel).grid(row=row,column=2)
    row += 1
    return row
def rowViewCheckbox(row,label,textvariable):
    Checkbutton(root, text=label, variable=textvariable).grid(row=row,column=0, sticky=W)
    row += 1
    return row


def closeDialog():
    if oltExcelPath == None or oltExcelPath.get() == '':
        showerror('error','The configuration file must be selected')
        return
    if cvlanStr == None or cvlanStr.get() == '':
        showerror('error','cvlan can not be null')
        return
    if gatewayStr == None or gatewayStr.get() == '':
        showerror('error','gateway can not be null')
        return
    if ftpServerStr == None or ftpServerStr.get() == '':
        showerror('error','ftpServer can not be null')
        return
    if ftpUserNameStr == None or ftpUserNameStr.get() == '':
        showerror('error','ftpUserName can not be null')
        return
    if ftpPasswordStr == None or ftpPasswordStr.get() == '':
        showerror('error','ftpPassword can not be null')
        return
    if imageFileNameStr == None or imageFileNameStr.get() == '':
        showerror('error','imageFileName can not be null')
        return
    if threadNumStr == None or threadNumStr.get() == '':
        showerror('error','threadNum can not be null')
        return
    if cmvlanIV == None or cmvlanIV.get() == '':
        showerror('error','cm vlan can not be null')
        return
    root.destroy()
    try:
        doUpgradeMud()
    except ValueError, e:
        msg = str(e)
        if "IP Address format was invalid" in msg:
            print "Excel中IP地址填写错误，可能是多了空行或者多了空格，请仔细检查"
        elif "has invalid prefix length" in msg:
            print "再或者网段地址填写成了具体的IP地址，请仔细检查"
        else :
            print "参数填写错误，请仔细检查各项参数设置，包括Excel"
        print 'traceback.format_exc():\n%s' % traceback.format_exc()

def doUpgradeMud():
    resultDialog = Tk()
    scrbar = Scrollbar(resultDialog)
    listView = ListView(resultDialog)
    listView["yscrollcommand"] = scrbar.set
    listView.grid(row=0, column=0, columnspan=2)
    cols = [{"key":"ip","width":100,"text":"IP"},
            {"key":"result","width":350,"text":"Result"},
            {"key":"clearResult","width":300,"text":"ClearResult"},
            {"key":"isAAA","width":100,"text":"是否开启AAA"},
            {"key":"userName","width":100,"text":"账号"},
            {"key":"password","width":100,"text":"密码"},
            {"key":"enablePassword","width":100,"text":"enable密码"}]
    listView.initColumn(cols)

    excel = oltExcelPath.get()
    cvlan = cvlanStr.get()
    gateway = gatewayStr.get()
    ftpServer = ftpServerStr.get()
    ftpUserName = ftpUserNameStr.get()
    ftpPassword = ftpPasswordStr.get()
    imageFileName = imageFileNameStr.get()
    threadNum = threadNumStr.get()
    version = versionStr.get()
    cmvlan = cmvlanIV.get()

    logPath = './log/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '/'
    os.makedirs(logPath)

    resultExcel = logPath + 'OltResult.xls'

    rb = xlrd.open_workbook(excel)
    wb = copy(rb)
    sheetCount = len(rb.sheets())
    for si in range(sheetCount):
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        sheetName = `si`
        sheetR = rb.sheet_by_index(si)
        sheetW = wb.get_sheet(si)
        nrows = sheetR.nrows
        ncols = sheetR.ncols
        wi = 0
        sheetW.write(wi, 5, 'upgrade Result')
        wi += 1
        for i in range(2, nrows):
            ip = sheetR.cell(i, 0).value
            isSsh = "是" == sheetR.cell(i, 1).value
            isAAA = "是" == sheetR.cell(i, 2).value
            username = sheetR.cell(i, 3).value
            password = sheetR.cell(i, 4).value
            enablePassword = sheetR.cell(i, 5).value
            ipMakerType = sheetR.cell(i, 6).value
            segmentIp = sheetR.cell(i, 7).value
            segmentMask = sheetR.cell(i, 8).value
            segmentGateway = sheetR.cell(i, 9).value
            segmentExcludeIpList = sheetR.cell(i, 10).value
            iplist = sheetR.cell(i, 11).value
            cmIpMask = sheetR.cell(i, 12).value
            cmIpGateway = sheetR.cell(i, 13).value
            ipMaker = IpMaker(ipMakerType,segmentIp,segmentMask,segmentGateway,segmentExcludeIpList,iplist,cmIpMask,cmIpGateway)
            upgradeCcmts = UpgradeCcmts()
            upgradeCcmts.connect(ip, isAAA, username, password, enablePassword, logPath, sheetW, i, cvlan, gateway,
                                 ftpServer, ftpUserName, ftpPassword, imageFileName,int(threadNum),version,cmvlan,listView,ipMaker,isSsh=isSsh)
            upgradeCcmts.setDaemon(True)
            upgradeCcmts.start()
    resultDialog.mainloop()
    wb.save(resultExcel)

##########################################arg dialog######################################################
root = Tk()
oltExcelPath = StringVar()
cvlanStr = StringVar()
gatewayStr = StringVar()
ftpServerStr = StringVar()
ftpUserNameStr = StringVar()
ftpPasswordStr = StringVar()
imageFileNameStr = StringVar()
threadNumStr = StringVar()
versionStr = StringVar()
cmvlanIV = IntVar()
cvlanStr.set('500')
gatewayStr.set('50')
ftpServerStr.set('10.30.30.242')
ftpUserNameStr.set('c')
ftpPasswordStr.set('c')
imageFileNameStr.set('c.bin')
threadNumStr.set('10')
versionStr.set('')
cmvlanIV.set(1)

row = 0
row = rowView(row,'OltExcel',oltExcelPath,fun=selectOltExcelPath)
row = rowView(row,'CVlan',cvlanStr)
row = rowView(row,'Gateway',gatewayStr,lastLabel='.254.0.1')
row = rowView(row,'Ftp Server',ftpServerStr)
row = rowView(row,'Ftp Username',ftpUserNameStr)
row = rowView(row,'Ftp Password',ftpPasswordStr)
row = rowView(row,'Image Name',imageFileNameStr)
row = rowView(row,'Thread count',threadNumStr)
row = rowView(row,'Target version',versionStr)
row = rowView(row,'CM vlan',cmvlanIV)
Button(root,text='complte',command=closeDialog).grid(row=row,column=1)
root.mainloop()
