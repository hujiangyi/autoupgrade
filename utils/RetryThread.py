#encoding:utf-8
from threading import *
import time

class RetryThread(Thread):
    def __init__(self,newThread):
        Thread.__init__(self)
        self.retryList = []
        self.newThread = newThread
    def run(self):
        while True:
            if len(self.retryList) != 0:
                arg = self.retryList.pop(0)
                args = arg['args']
                step = arg['step']
                self.newThread(*args,step=step)
            else :
                time.sleep(5)
