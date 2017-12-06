# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,bfs
from getcmds_traversal import breadthFirstTraversalList
from mydb import getconn


def get_room_list_byRName(ref_rid,rname):
    depth = 15
    nodes = []
    p = MudRoomSearchProblem(ref_rid,None)
    nodes = breadthFirstTraversalList(p,nodes,depth)
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT rid from roominfo where rname=?',(rname.decode("utf8"),))
    rows = cursor.fetchall()
    conn.close()    
    
    if len(rows)==0:
        return []
       
    rids = []
    for n in nodes:
        for row in rows:        
            if row[0] == n.status:
                rids.append(n.status)
            
    return rids 
    
def main(args):
    ref_rid = args[1].decode("gb18030").encode("utf8");
    rname = args[2].decode("gb18030").encode("utf8");
    if len(args)==2:
        depth = 5
    else:
        depth = int(args[3].decode("gb18030").encode("utf8"));
   
#    ref_rid = "978dd91452cfa9ca80d8816822786374" 
#    rname = "北大街"
#    depth =0
#    
    rids = get_room_list_byRName(ref_rid,rname)
#    print rids
    #test:
#    print area,rname
#    print ridlist
    #####
    #points traversal:
    if len(rids) > 0:
        nodes = []
        for rid in rids:
            p = MudRoomSearchProblem(rid,None)
#            nodes = depthFirstTraversalList(p,nodes,depth)
            nodes = breadthFirstTraversalList(p,nodes,depth)
        
        nodes.append(nodes[0])
       
#        print [node.status for node in nodes]
        i = 0
        ret = ""
        while i<len(nodes)-1:
            init_rid = nodes[i].status
            goal_rid = nodes[i+1].status
            p = MudRoomSearchProblem(init_rid,goal_rid)
            actions,_,_=bfs(p)        
            for act in actions:
                ret = ret + act + ";"
            i = i + 1
        retlist = ret.split(";")
       
        for a in retlist[:-1]:
            print a
        
    

       
if __name__=="__main__":
    main(sys.argv)
