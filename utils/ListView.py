#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from threading import Lock
from ttk import *

class ListView(Treeview):
    def initColumn(self,cols):
        #self["show"] = "headings"
        self["height"] = 30
        keys = []
        self.cols = {}
        self.rows={}
        self.treeLock = Lock()
        for i,col in enumerate(cols):
            keys.append(col["key"])
        self["columns"] = tuple(keys)
        for i,col in enumerate(cols):
            self.column(col["key"],width=col["width"])
            self.heading(col["key"],text=col["text"])
            col["index"] = i
            self.cols[col["key"]] = col

    def insertRow(self,row):
        self.treeLock.acquire()
        try :
            identifyKey = row[row["identifyKey"]]
            if self.rows.has_key(identifyKey) :
                for key,col in self.cols.items():
                    value = row[key]
                    self.setData(identifyKey,key,value)
                    return
            values = ['' for i in range(0, len(self.cols))]
            for key,col in self.cols.items():
                if row.has_key(key) :
                    value = row[key]
                    values[col["index"]]=value
            rowKey = self.insert("","end",values=tuple(values))
            rowData = {}
            rowData["key"] = rowKey
            rowData["data"] = values
            self.rows[identifyKey] = rowData
        finally:
            self.treeLock.release()

    def insertChildRow(self,parentKey,row):
        self.treeLock.acquire()
        try :
            if self.rows.has_key(parentKey):
                rd = self.rows[parentKey]
                parentItemKey = rd['key']
                values = ['' for i in range(0, len(self.cols))]
                for key,col in self.cols.items():
                    if row.has_key(key) :
                        value = row[key]
                        values[col["index"]]=value
                identifyKey = parentKey + "_" + row[row["identifyKey"]]
                rowKey = self.insert(parentItemKey,"end",values=tuple(values))
                rowData = {}
                rowData["key"] = rowKey
                rowData["data"] = values
                self.rows[identifyKey] = rowData
        finally:
            self.treeLock.release()

    def setData(self,identifyKey,colKey,value):
        self.treeLock.acquire()
        try :
            if self.rows.has_key(identifyKey) :
                rowData = self.rows[identifyKey]
                rowKey = rowData["key"]
                values = rowData["data"]
                col = self.cols[colKey]
                values[col["index"]] = value
                self.set(rowKey,colKey,value)
        finally:
            self.treeLock.release()