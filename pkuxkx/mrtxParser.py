# -*- coding: utf-8 -*-
import sys
import pdb
import re
import pickle

class MyZs:
    def __init__(self, words):
        self.words = words        
        self.bigwords = bigWordsParse(words)        
        self.score = calulateScore(self.words,self.bigwords)
    def hasBigwords(self):
        if len(self.bigwords)>0:
            return True
        else:
            return False
    def getWords(self):
        return self.words
    def getBigWords(self):
        return self.bigwords
    def getScore(self):
        return self.score

def bigWordsParse(line):
    r1 = re.compile(r"[(.*?)]".decode("utf8"))
    r2 = re.compile(r"「(.*?)」".decode("utf8"))
    r3 = re.compile(r"‘(.*?)’".decode("utf8"))   
    ret = ""
    if r3.search(line):
        s = r3.search(line)
        ss = s.group(1)
        ret = ss
    if r1.search(line):
        s = r1.search(line)
        ss = s.group(1)
        ret = ss
    if r2.search(line):
        s = r2.search(line)
        ss = s.group(1)
        ret = ss
    return ret
    
def calulateScore(words,bigwords):
    score = 0
    score = score + len(words)
    score = score + 20*len(bigwords)
    return score
        
def tripWords(line):
    words2trip = "大英雄盖世杰豪，；。.()".decode("utf8")
    for w in words2trip:
        line = line.replace(w,'')
    return line
    
def main(args):
    zsfile = open("./tintin/myscripts/pkuxkx/txzs.tin")
#    zsfile = open("txzs.tin")
    lines = zsfile.readlines()
    zslist = []
    ##pdb.set_trace()
    rr = re.compile(r"^慕容复在你的耳边悄声说道：(.*)".decode("utf8"))
    for line in lines:
        if rr.search(line.decode("gb18030")):
            s = rr.search(line.decode("gb18030"))
            ss = s.group(1)
            sss = tripWords(ss) 
            zs = MyZs(sss)
            zslist.append(zs)
    
    output = open('./tintin/myscripts/pkuxkx/mrtx_data.pkl', 'wb')
    pickle.dump(zslist, output)
    output.close()        
    print 1
    
       
if __name__=="__main__":
    main(sys.argv)
