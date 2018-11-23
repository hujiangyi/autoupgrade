#encoding:utf-8
import ConfigParser
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
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
encode = 'UTF-8'
def log(msg):
    print msg.decode('UTF-8').encode(encode)

def getConfig(section,key,default):
    try:
        config = ConfigParser.ConfigParser()
        config.read('config.conf')
        return config.get(section, key)
    except BaseException, msg:
        return default

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
            log("Excel中IP地址填写错误，可能是多了空行或者多了空格，请仔细检查")
        elif "has invalid prefix length" in msg:
            log("再或者网段地址填写成了具体的IP地址，请仔细检查")
        else :
            log("参数填写错误，请仔细检查各项参数设置，包括Excel")
        log('traceback.format_exc():\n%s' % traceback.format_exc())

def doUpgradeMud():
    resultDialog = Tk()
    scrbar = Scrollbar(resultDialog)
    listView = ListView(resultDialog)
    listView["yscrollcommand"] = scrbar.set
    listView.grid(row=0, column=0, columnspan=2)
    cols = [{"key":"ip","width":100,"text":"IP"},
            {"key":"result","width":350,"text":"Result"},
            {"key":"clearResult","width":300,"text":"ClearResult"},
            {"key":"faildReason","width":100,"text":"升级失败原因"},
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
        log('%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
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
            isSshStr = sheetR.cell(i, 1).value
            isAAAStr = sheetR.cell(i, 2).value
            isSsh = isSshStr == '是'
            isAAA = isAAAStr == '是'
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
encode = getConfig("system","encode","UTF-8")
cvlanConfig = getConfig("default","cvlan","500")
gatewayConfig = getConfig("default","gateway","50")
ftpServerConfig = getConfig("default","ftpServer","172.17.2.2")
ftpUserConfig = getConfig("default","ftpUser","c")
ftpPwdConfig = getConfig("default","ftpPwd","c")
binNameConfig = getConfig("default","binName","c.bin")
threadNumConfig = getConfig("default","threadNum","10")
targetVersionConfig = getConfig("default","targetVersion","")
cmvlanConfig = getConfig("default","cmvlan","1")
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
cvlanStr.set(int(cvlanConfig))
gatewayStr.set(gatewayConfig)
ftpServerStr.set(ftpServerConfig)
ftpUserNameStr.set(ftpUserConfig)
ftpPasswordStr.set(ftpPwdConfig)
imageFileNameStr.set(binNameConfig)
threadNumStr.set(threadNumConfig)
versionStr.set(targetVersionConfig)
cmvlanIV.set(int(cmvlanConfig))

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
