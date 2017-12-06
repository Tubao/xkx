# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,MyNode,bfs
import re
import Queue
from mydb import getconn

def depthFirstTraversalList(problem,explored,depth = 3):        
    frontier = Queue.LifoQueue()       
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return explored
        node = frontier.get()
        explored.append(node)
        if node.getDepth()>=depth:
            continue        
        for successor in problem.getTraversalSuccessors(node.status):
            s_status = successor[0]
            s_d = successor[1]
            s_c = successor[2]
            flag = True
            for n in frontier.queue:
                if n.status == s_status:
                    flag = False
            for n in explored:
                if n.status == s_status:
                    flag = False
            if flag:
                frontier.put(MyNode(s_status,node,s_d,s_c))

def loc_split(loc):
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select cname from area_name_map')
    rows = cursor.fetchall()
    conn.close()    
    for row in rows:
        regexp = r'^'+row[0].encode("utf8") + '(.*)'        
        if re.search(regexp,loc):            
            s = re.search(regexp,loc)            
            return  (row[0].encode("utf8"),s.group(1))    
    return (None,None)
    
def get_room_list(area,rname):
    ret = []
    if area is None:
        return ret
    conn = getconn()
    cursor = conn.cursor()
    if len(rname)>0:
        cursor.execute('SELECT t2.rid  FROM area_name_map t1,roominfo t2 where t1.area=t2.area and t1.cname=? and t2.rname=?',(area.decode("utf8"),rname.decode("utf8")))
    else:
        cursor.execute('SELECT t2.rid  FROM area_name_map t1,roominfo t2 where t1.area=t2.area and t1.cname=?',(area.decode("utf8"),))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        ret.append(row[0])
    return ret
    
def main(args):
    loc = args[1].decode("gb18030").encode("utf8");
    if len(args)==1:
        depth = 3
    else:
        depth = int(args[2].decode("gb18030").encode("utf8"));
#    loc='扬州打铁铺'
#    depth=2
    
    (area,rname) = loc_split(loc)
    
    ridlist = get_room_list(area,rname)
    
    #test:
#    print area,rname
#    print ridlist
    #####
    if len(ridlist)>0:        
        nodes = []
        for rid in ridlist:
            p = MudRoomSearchProblem(rid,None)
            nodes = depthFirstTraversalList(p,nodes,depth)
        
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
