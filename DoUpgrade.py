#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import *
import xlrd
from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from xlutils.copy import copy
from UpgradeOlt.tools.UpgradeOltFtpClient import *
from utils.ListView import *
from utils.RetryThread import *

def newThread(isAAA, username, password, enablePassword, versionPath, logPath, sheetW, i, listView,downloadFlie = True,upgradeBootrom = True,writeFile=True,reboot=True,host=None,step=0):
    upgradeClient = UpgradeOltFtpClient()
    upgradeClient.connect(host, isAAA, username, password, enablePassword, versionPath, logPath, sheetW, i, listView,downloadFlie=downloadFlie,upgradeBootrom=upgradeBootrom,writeFile=writeFile,reboot=reboot)
    upgradeClient.step = step
    upgradeClient.setDaemon(True)
    upgradeClient.start()
    return upgradeClient

retryThread = RetryThread(newThread)
retryThread.setDaemon(True)
retryThread.start()
root = Tk()
oltExcelPath = StringVar()
imagePath = StringVar()
downloadFlie = IntVar()
upgradeBootrom = IntVar()
writeFile = IntVar()
reboot = IntVar()

downloadFlie.set(1)
upgradeBootrom.set(0)
writeFile.set(0)
reboot.set(1)

def selectOltExcelPath():
    path_ = askopenfilename()
    oltExcelPath.set(path_)
def selectImagePath():
    path_ = askdirectory()
    imagePath.set(path_)

def doUpgrade() :
    resultDialog = Tk()
    scrbar = Scrollbar(resultDialog)
    listView = ListView(resultDialog)
    listView["yscrollcommand"] = scrbar.set
    listView.grid(row=0, column=0, columnspan=2)
    cols = [{"key":"ip","width":100,"text":"IP"},
            {"key":"result","width":400,"text":"Result"},
            {"key":"isAAA","width":100,"text":"是否开启AAA"},
            {"key":"userName","width":100,"text":"账号"},
            {"key":"password","width":100,"text":"密码"},
            {"key":"enablePassword","width":100,"text":"enable密码"}]
    listView.initColumn(cols)
    excel = oltExcelPath.get()
    versionPath = imagePath.get()

    downloadFlieValue = bool(downloadFlie.get())
    upgradeBootromValue = bool(upgradeBootrom.get())
    writeFileValue = bool(writeFile.get())
    rebootValue = bool(reboot.get())

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
        for i in range(1,nrows):
            ip = sheetR.cell(i, 0).value
            isAAA = sheetR.cell(i, 1).value
            username = sheetR.cell(i, 2).value
            password = sheetR.cell(i, 3).value
            enablePassword = sheetR.cell(i, 4).value

            upgradeClient = newThread(isAAA, username, password, enablePassword, versionPath, logPath, sheetW, i, listView,downloadFlie=downloadFlieValue,upgradeBootrom=upgradeBootromValue,writeFile=writeFileValue,reboot=rebootValue,host=ip)
            upgradeClient.setRetryThreadR(retryThread)
    resultDialog.mainloop()
    wb.save(resultExcel)

def closeDialog():
    if oltExcelPath == None or oltExcelPath.get() == '':
        showerror('error','The configuration file must be selected')
        return
    if imagePath == None or imagePath.get() == '':
        showerror('error','The image directory must be selected')
        return
    root.destroy()
    doUpgrade()

def getValue(globalValue,value):
    re = value
    if value == None or '' == value:
        re = globalValue
    return re

Label(root,text='OltExcel').grid(row=0,column=0)
Entry(root,textvariable=oltExcelPath).grid(row=0,column=1)
Button(root,text='select',command=selectOltExcelPath).grid(row=0,column=2)

Label(root,text='ImagePath').grid(row=1,column=0)
Entry(root,textvariable=imagePath).grid(row=1,column=1)
Button(root,text='select',command=selectImagePath).grid(row=1,column=2)

Checkbutton(root, text="是否下载镜像", variable=downloadFlie).grid(row=2,column=0,columnspan=2, sticky=W)
Checkbutton(root, text="是否升级BOOTROM", variable=upgradeBootrom).grid(row=3,column=0,columnspan=2, sticky=W)
Checkbutton(root, text="是否WriteFile", variable=writeFile).grid(row=4,column=0,columnspan=2, sticky=W)
Checkbutton(root, text="是否Reboot", variable=reboot).grid(row=5,column=0,columnspan=2, sticky=W)

Button(root,text='complte',command=closeDialog).grid(row=6,column=1)
root.mainloop()