# -*- coding: utf-8 -*-
import sys
import re

def main(args):
    s = args[1].decode("gb18030");
    spliter = args[2].decode("gb18030");
    p = re.compile(spliter)
    retlist = p.split(s)

    for a in retlist:
        print a

       
if __name__=="__main__":
    main(sys.argv)
