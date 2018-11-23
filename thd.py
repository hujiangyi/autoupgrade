#encoding:utf-8
from threading import *
import time
from Tkinter import *
from utils.ListView import *

class MyThread(Thread):
    def __init__(self,name,listView):
        Thread.__init__(self)
        self.name = name
        self.listView = listView
    def run(self):
        row = {"identifyKey": "ip", "ip": self.name, "mac": "012345678912"}
        listView.insertRow(row)
        print self.name, 'start'
        time.sleep(20)
        print self.name, 'end'
        listView.setData(self.name,'mac','over')
def addData():
    print 1
def modifyData():
    print 1

resultDialog = Tk()
Button(resultDialog, text='add', command=addData).grid(row=0, column=0, sticky=W)
Button(resultDialog, text='modify', command=modifyData).grid(row=0, column=1, sticky=E)
listView = ListView(resultDialog)
listView.grid(row=1, column=0, columnspan=2)
cols = [{"key":"ip","width":100,"text":"IP"},{"key":"mac","width":100,"text":"Mac"}]
listView.initColumn(cols)
for i in range(0,10):
    t = MyThread('name'+`i`,listView)
    t.setDaemon(True)
    t.start()
    time.sleep(1)

resultDialog.mainloop()