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
from tools.UpgradeOltFtpClient import *
from xlutils.copy import copy

root = Tk()
oltExcelPath = StringVar()
logPath = StringVar()
def selectOltExcelPath():
    path_ = askopenfilename()
    oltExcelPath.set(path_)
def selectLogPath():
    path_ = askdirectory()
    logPath.set(path_)
def closeDialog():
    if oltExcelPath == None or oltExcelPath.get() == '':
        showerror('error','The configuration file must be selected')
        return
    if logPath == None or logPath.get() == '':
        showerror('error','The log directory must be selected')
        return
    root.destroy()

def getValue(globalValue,value):
    re = value
    if value == None or '' == value:
        re = globalValue
    return re

Label(root,text='OltExcel').grid(row=0,column=0)
Entry(root,textvariable=oltExcelPath).grid(row=0,column=1)
Button(root,text='select',command=selectOltExcelPath).grid(row=0,column=2)
Label(root,text='LogPath').grid(row=1,column=0)
Entry(root,textvariable=logPath).grid(row=1,column=1)
Button(root,text='select',command=selectLogPath).grid(row=1,column=2)
Button(root,text='complte',command=closeDialog).grid(row=2,column=1)
root.mainloop()

excel = oltExcelPath.get()
logPath = logPath.get()
logPath += '/'

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
    #sheetW.write(wi, 5, 'upgrade Result')
    wi += 1
    thread_list = []
    for i in range(1,nrows):
        ip = sheetR.cell(i, 0).value
        isAAA = sheetR.cell(i, 1).value
        username = sheetR.cell(i, 2).value
        password = sheetR.cell(i, 3).value
        enablePassword = sheetR.cell(i, 4).value
        upgradeClient = UpgradeOltFtpClient()
        upgradeClient.connect(ip,isAAA,username,password,enablePassword,'',logPath,sheetW,i)
        t = Thread(target=upgradeClient.doCollectData())
        thread_list.append(t)
        t.setDaemon(True)
        t.start()
    for t in thread_list:
        t.join()
#wb.save(resultExcel)