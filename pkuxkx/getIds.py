# -*- coding: utf-8 -*-
import sys
import re
import pdb

def main(args):
    #pdb.set_trace()
    lines = args[1].decode("gb18030").encode("utf8").split("|||")     
    #lines = "|||在这个房间中, 生物及物品的(英文)名称如下 :||||||下课行               = davidss|||中年道长             = zhongnian daozhang, daozhang|||谷虚莱�             = guxu daozhang, guxu|||神武功德录           = board|||小喽罗               = xiao louluo, louluo|||>".split("|||")
    
    p = re.compile(r"^(\S+)\s*=\s*(.+?)$")
    for line in lines:
        if p.match(line):
            s = p.match(line)            
            ps = re.compile(r",")
            mylist = ps.split(s.group(2).strip(" "))
            npc_ename = mylist[-1]
            npc_cname=s.group(1)            
            print(npc_cname.decode("utf8").encode("gb18030"))
            print(npc_ename.decode("utf8").encode("gb18030"))         
           
                
if __name__=="__main__":
    main(sys.argv)
