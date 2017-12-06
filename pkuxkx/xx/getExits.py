# -*- coding: utf-8 -*-
import sys
import re
import pdb
import random
def main(args):
    #pdb.set_trace()
    lines = args[1].decode("gb18030").encode("utf8").split("|||")
    for line in lines:        
        if re.search(r"^\s*这里.*?出口是 (.*?)。",line):
            s = re.search(r"^\s*这里.*?出口是 (.*?)。",line)
            ss = s.group(1)
            p = re.compile(r"、| 和 ")
            ret = p.split(ss)
            random.shuffle(ret)
            for r in ret:
                print(r)
                
if __name__=="__main__":
    main(sys.argv)