# -*- coding: utf-8 -*-
from getcmds_traversal_rid import get_room_list_byRName
import sys

def main(args):
    ref_rid = args[1].decode("gb18030").encode("utf8");
    rname = args[2].decode("gb18030").encode("utf8");


   
#    ref_rid = "978dd91452cfa9ca80d8816822786374" 
#    rname = "西大街"

    
    rids = get_room_list_byRName(ref_rid,rname)
    if len(rids)>0:
        print rids[0]
    else:
        print 0

if __name__=="__main__":
    main(sys.argv)