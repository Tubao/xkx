# -*- coding: utf-8 -*-
import sys
import pdb
import re
import pickle
from mrtxParser import MyZs,bigWordsParse,calulateScore

def tripWords(npcname,line):
    words2trip = "你，；。.".decode("utf8")
    line = line.replace(npcname,'')
    for w in words2trip:
        line = line.replace(w,'')
    return line
    
def main(args):
    npcname = args[1].decode("gb18030")
    zs = args[2].decode("gb18030")
    THRESHOLD = 0.55
#    npcname='花莎凤'.decode('utf8')
#    zs = '花莎凤鼓起全部气力于左拳，只听见骨节爆响的声音，一招「纵死侠骨香」迅猛地向你击去！你身形向后一纵，使出一招「飘然出尘」，避过了花莎凤的攻击。#3.37M,719370,2912,4132,2502,5004'.decode('utf8')
    sss = tripWords(npcname,zs)
    zsobj = MyZs(sss)
    
    pkl_file = open('./tintin/myscripts/pkuxkx/mrtx_data.pkl', 'rb')
#    pkl_file = open('mrtx_data.pkl', 'rb')
    zslist = pickle.load(pkl_file)   
    pkl_file.close()     
    remainlist = []
    i = 0
    maxscore = 0
    maxscore_zs = None
    while i < len(zslist):
        myzs = zslist[i]
        score = 0
        for w in myzs.getWords():
            if w in zsobj.getWords():
                score = score + 1
        if myzs.hasBigwords():
            for w in myzs.getBigWords():
                if w in zsobj.getBigWords():
                    score = score + 20
        score = (score+0.01)/myzs.getScore()
        if maxscore<score:
            if maxscore_zs is not None:
                remainlist.append(maxscore_zs)
            maxscore = score
            maxscore_zs = myzs
        else:
            remainlist.append(myzs)
        i = i + 1
        
    if maxscore > THRESHOLD:
        output = open('./tintin/myscripts/pkuxkx/mrtx_data.pkl', 'wb')
        pickle.dump(remainlist, output)
        output.close() 
        if len(remainlist) == 0:
            print 2
        else:
            print 1            
    else:
        output = open('./tintin/myscripts/pkuxkx/mrtx_data.pkl', 'wb')
        pickle.dump(zslist, output)
        output.close()      
        print 0
        print maxscore
#    print maxscore,maxscore_zs.getWords()
#    for zs in remainlist:
#        print zs.getWords()
    
       
if __name__=="__main__":
    main(sys.argv)
