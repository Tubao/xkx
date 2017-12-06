# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,MyNode,bfs
import re
import Queue
from mydb import getconn
from getcmds_traversal import depthFirstTraversalList_inArea

def depthFirstTraversalList(problem,explored,depth = 3):        
    frontier = Queue.LifoQueue()       
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return explored
        node = frontier.get()
        flag = True
        for n in explored:
                if n.status == node.status:
                    flag = False
        if flag:
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
def breadthFirstTraversalList(problem,explored,depth = 3):        
    frontier = Queue.Queue()  
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return explored
        node = frontier.get()
        flag = True
        for n in explored:
                if n.status == node.status:
                    flag = False
        if flag:
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

def getAreaRooms_py(area,exp_depth=3):
    arooms = []
    brooms = []
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT t2.rid  FROM area_name_map t1,(select rid,rname,py_name,ifnull(t_area,area) as tarea from v_traversal_roominfo) t2 where t1.area=t2.tarea and t1.py_name=?',(area.decode("utf8"),))
    rows = cursor.fetchall()
    for row in rows:
        arooms.append(row[0])
    cursor.execute('SELECT t2.rid  FROM area_name_map t1,(select rid,rname,py_name,ifnull(t_area,area) as tarea from v_traversal_roominfo) t2,v_roomrel_nextarea t3 where t2.rid=t3.rid and t1.area=t2.tarea and t3.next_area_py<>? and t1.py_name=?',(area.decode("utf8"),area.decode("utf8")))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        if row[0] not in brooms:
            brooms.append(row[0])
    
    if len(brooms)>0:        
        nodes = []
        for rid in brooms:
            p = MudRoomSearchProblem(rid,None)
#            nodes = depthFirstTraversalList(p,nodes,depth)
            nodes = breadthFirstTraversalList(p,nodes,exp_depth)
        for node in nodes:
             if node.status not in arooms:
                 arooms.append(node.status)
     
    return (arooms,brooms)
    
def get_room_list_bypy(area,rname):       
    ret = []
    if area is None:
        return ret
    conn = getconn()
    cursor = conn.cursor()
    (arooms,brooms) = getAreaRooms_py(area)
    if len(rname)>0:        
        cursor.execute('SELECT rid,rname from roominfo where py_name=?',(rname.decode("utf8"),))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            if row[0] in arooms:
                ret.append(row[0])   
    else:
        ret = arooms    
    
    return (ret,arooms,brooms)
    
    
def main(args):
    loc = args[1].decode("gb18030").encode("utf8");
    if len(args)==1:
        depth = 3
    else:
        depth = int(args[2].decode("gb18030").encode("utf8"));
#    loc='扬州打铁铺'
#    depth=2
    
    ss = re.split("\s+",loc)  
    (area,rname) = ("","")
    if len(ss) == 1:
        area = ss[0]
    if len(ss) > 1 :
        (area,rname) = (ss[0],ss[1])
    (ridlist,arooms,brooms) = get_room_list_bypy(area,rname)
    
    #points traversal:
    if len(rname)>0 and len(ridlist)>0:        
        nodes = []
        for rid in ridlist:
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
        
    #area traversal:
    if len(rname)==0:   
        #use brooms[0] as start point
        startp = ridlist[0]
        if len(brooms)>0:
            startp = brooms[0]
        nodes = []
        p = MudRoomSearchProblem(startp,None)
        nodes = depthFirstTraversalList_inArea(p,arooms)
        
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
