# -*- coding: UTF-8 -*-

path = {
    'hz' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'sw', 'w', 'sw', 'w', 'w', 'done'], 
    'lj' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'sw', 'sw', 's', 'enter', 'done'],
    'jz' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 's', 'nw', 'n', 'nw', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'nw', 'nd', 'n', 'n', 'n', 'done'], 
    'gy' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'nw', 'w', 'w', 'w', 'w', 'w', 'w', 'nw', 'ne', 'se', 'n', 'w', 'n', 'e', 'e', 'done'], 
    'sz' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'n', 'n', 'n', 'n', 'n', 'done'], 
    'ywm' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'e', 'n', 'e', 'done'], 
    'ys' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'n', 'e', 'se', 'ne', 'e', 'ne', 'ne', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'done'],
    'jx' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'n', 'e', 'done'], 
    'qz' : ['s', 's', 'w', 'w', 'w', 'w', 'sw', 'sw', 's', 's', 'sw', 'sw', 'sw', 'done'], 
    'nc' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 's', 'nw', 'n', 'nw', 'n', 'n', 'n', 'n', 'n', 'done'], 
    'zj' : ['s', 's', 'w', 'n', 'n', 'n', 'nu', 'nw', 'nw', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'nw', 'n', 'ne', 'ne', 'n', 'nw', 'nw', 'w', 'w', 'w', 'w', 'n', 'done'], 
}

class Tuiche(object):
    def __init__(self):
        self.where = ''
        self.point = 0
    def sendcmd(self, cmd):
        print "sendcmd (pkuxkx) " + cmd
    def next(self):
        self.sendcmd('g' + path[self.where][self.point])
        self.point = self.point + 1
    def decr(self):
        self.point = self.point - 1
    def Hangzhou(self):
        self.where = 'hz'
        self.point = 0
    def Lujia(self):
        self.where = 'lj'
        self.point = 0
    def Jiangzhou(self):
        self.where = 'jz'
        self.point = 0
    def Guiyun(self):
        self.where = 'gy'
        self.point = 0
    def Suzhou(self):
        self.where = 'sz'
        self.point = 0
    def Yuewangmu(self):
        self.where = 'ywm'
        self.point = 0
    def Yashan(self):
        self.where = 'ys'
        self.point = 0
    def Quanzhou(self):
        self.where = 'qz'
        self.point = 0
    def Nanchang(self):
        self.where = 'nc'
        self.point = 0
    def Zhenjiang(self):
        self.where = 'zj'
        self.point = 0
    def Jiaxing(self):
        self.where = 'jx'
        self.point = 0
