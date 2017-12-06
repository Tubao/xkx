# -*- coding: utf-8 -*-
import sys
import re
import pdb
def to_numbers(ch):
    n_dict = {"一":1,\
              "二":2,\
              "三":3,\
              "四":4,\
              "五":5,\
              "六":6,\
              "七":7,\
              "八":8,\
              "九":9,\
              "十":10}
    return n_dict[ch]

def main(args):
    #pdb.set_trace()
    lines = args[1].decode("gb18030").encode("utf8").split("|||")     
    p = re.compile(r"^\s*((一|二|三|四|五|六|七|八|九|十)(位|只))?(.*?)\((.*?)\)( <(.*?)>)?$")
    for line in lines:
        if p.match(line):
            s = p.match(line)
            npc_num = 1
            if s.group(2) is not None:
                npc_num = to_numbers(s.group(2))
            ps = re.compile(r" |「|」")
            mylist = ps.split(s.group(4).strip(" "))
            npc_title1=""
            npc_title2=""
            npc_title3=""
            npc_cname=""
            ts = []
            for t in mylist:
                if t=="":
                    continue
                ts.append(t)
            if len(ts) == 4:
                npc_title1 = ts[0]
                npc_title2 = ts[1]
                npc_title3 = ts[2]
                npc_cname = ts[3]
            if len(ts) == 3:
                npc_title1 = ts[0]
                npc_title2 = ts[1]                
                npc_cname = ts[2]
            if len(ts) == 2:
                npc_title1 = ts[0]                             
                npc_cname = ts[1]
            if len(ts) == 1:                           
                npc_cname = ts[0]
            
            npc_ename = s.group(5)
            npc_status = s.group(7)
            if npc_status is None:
                npc_status = "normal"
            print(npc_num)
            print(npc_title1.decode("utf8").encode("gb18030"))
            print(npc_title2.decode("utf8").encode("gb18030"))
            print(npc_title3.decode("utf8").encode("gb18030"))
            print(npc_cname.decode("utf8").encode("gb18030"))
            print(npc_ename.decode("utf8").encode("gb18030"))
            print(npc_status.decode("utf8").encode("gb18030"))
            
                
if __name__=="__main__":
    main(sys.argv)