# -*- coding: utf-8 -*-
import sys
import re
import pdb

def main(args):
    w1 = args[1].decode("gb18030").encode("utf8")
    w2 = args[2].decode("gb18030").encode("utf8")
    
    if len(w1)!=len(w2):
        print 0        
    else:
        flag = True
        for w in w2:
            if w not in w1:
                flag = False
                break
            
        if flag:
            print 1
        else:
            print 0   
                
if __name__=="__main__":
    main(sys.argv)