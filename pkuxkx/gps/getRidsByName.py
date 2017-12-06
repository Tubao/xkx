# -*- coding: utf-8 -*-
from getcmds_traversal import loc_split,get_room_list
import sys

def main(args):
    loc = args[1].decode("gb18030").encode("utf8");

#    loc='少林寺鼓楼二层'    
    
    (area,rname) = loc_split(loc)
    (ridlist,_,brooms) = get_room_list(area,rname)
    ret = []
    if len(rname)>0 or len(brooms)==0:    
        ret = ridlist 
    else:
        ret.append(brooms[0])
    for rid in ret:
        print rid

if __name__=="__main__":
    main(sys.argv)