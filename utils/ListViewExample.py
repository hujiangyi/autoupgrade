#encoding:utf-8
from Tkinter import *
from ListView import *

root = Tk()

def addData():
    print 1
def modifyData():
    print 1
Button(root,text='add',command=addData).grid(row=0,column=0,sticky=W)
Button(root,text='modify',command=modifyData).grid(row=0,column=1,sticky=E)
tree = ListView(root)
tree.grid(row=1,column=0,columnspan=2)

cols = [{"key":"ip","width":100,"text":"IP"},{"key":"mac","width":100,"text":"Mac"}]
tree.initColumn(cols)
row={"identifyKey":"ip","ip":"172.17.2.150","mac":"012345678912"}
tree.insertRow(row)
row={"identifyKey":"ip","ip":"172.17.2.152","mac":"012345678913"}
tree.insertRow(row)

root.mainloop()