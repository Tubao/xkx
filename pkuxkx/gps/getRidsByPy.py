# -*- coding: utf-8 -*-
from getcmds_ptraversal import get_room_list_bypy
import sys
import re

def main(args):
    loc = args[1].decode("gb18030").encode("utf8");

#    loc='saols gulec'    
    
    ss = re.split("\s+",loc)  
    (area,rname) = ("","")
    if len(ss) == 1:
        area = ss[0]
    if len(ss) > 1 :
        (area,rname) = (ss[0],ss[1])    
    (ridlist,_,brooms) = get_room_list_bypy(area,rname)    
    ret = []
    if len(rname)>0 or len(brooms)==0:    
        ret = ridlist 
    else:
        ret.append(brooms[0])
    for rid in ret:
        print rid

if __name__=="__main__":
    main(sys.argv)