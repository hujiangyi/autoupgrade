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

from UpgradeOlt.tools.PingTest import PingTest
from xlutils.copy import copy
from utils.ListView import *


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


def closeDialog():
    root.destroy()
    doUpgradeMud()

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
        for i in range(1, nrows):
            ip = sheetR.cell(i, 0).value
            isAAA = sheetR.cell(i, 1).value
            userName = sheetR.cell(i, 2).value
            password = sheetR.cell(i, 3).value
            enablePassword = sheetR.cell(i, 4).value
            cmip = sheetR.cell(i, 5).value
            mask = sheetR.cell(i, 6).value
            cmgateway = sheetR.cell(i, 7).value
            pingTest = PingTest()
            pingTest.connect(ip,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,i,listView)

            row = {"identifyKey": "ip",
                   "ip": pingTest.host,
                   "result": "start",
                   "isAAA": pingTest.isAAA == '1',
                   "userName": pingTest.userName,
                   "password": pingTest.password,
                   "enablePassword": pingTest.enablePassword}
            pingTest.listView.insertRow(row)
            pingTest.doTelnet()
            pingTest.send('end')
            str = pingTest.readuntil('#')
            print str
            re = pingTest.ping('50.2.4.1')
            print re
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

row = 0
row = rowView(row,'OltExcel',oltExcelPath,fun=selectOltExcelPath)
row = rowView(row,'CVlan',cvlanStr)
row = rowView(row,'Gateway',gatewayStr,lastLabel='.254.0.1')
row = rowView(row,'Ftp Server',ftpServerStr)
row = rowView(row,'Ftp Username',ftpUserNameStr)
row = rowView(row,'Ftp Password',ftpPasswordStr)
row = rowView(row,'Image Name',imageFileNameStr)
Button(root,text='complte',command=closeDialog).grid(row=row,column=1)
root.mainloop()
