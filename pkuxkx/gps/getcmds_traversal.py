# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,MyNode,bfs
import re
import Queue
from mydb import getconn
def depthFirstTraversalList_inArea(problem,arooms,depth = 50):        
    frontier = Queue.LifoQueue()      
    explored = []
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return explored
        node = frontier.get()        
        if node.getDepth()>=depth or node.status not in arooms:
            continue 
        flag = True
        for n in explored:
                if n.status == node.status:
                    flag = False          
        if flag:
            explored.append(node)
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
def loc_split(loc):
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select cname from area_name_map')
    rows = cursor.fetchall()
    
    for row in rows:
        regexp = r'^'+row[0].encode("utf8") + '(.*)'        
        if re.search(regexp,loc):            
            s = re.search(regexp,loc)
            area = row[0].encode("utf8")
            rname = s.group(1)
            if len(rname)>0:
                cursor.execute('SELECT count(1) FROM area_name_map t1,(select rid,rname,ifnull(t_area,area) as tarea from roominfo) t2 where t1.area=t2.tarea and t1.cname=? and t2.rname=?',(area.decode("utf8"),rname.decode("utf8")))
            else:
                cursor.execute('SELECT count(1) FROM area_name_map t1,(select rid,rname,ifnull(t_area,area) as tarea from roominfo) t2 where t1.area=t2.tarea and t1.cname=?',(area.decode("utf8"),))
            row1 = cursor.fetchone()
            if int(row1[0]) == 0:
                continue
            else:
                conn.close()
                return  (area,rname)    
    conn.close()    
    return (None,None)
    
def get_room_list(area,rname):
    ret = []
    if area is None:
        return ret
    conn = getconn()
    cursor = conn.cursor()
    (arooms,brooms) = getAreaRooms(area)
    if len(rname)>0:    
        cursor.execute('SELECT rid,rname from roominfo where rname=? and area=?',(rname.decode("utf8"),area.decode("utf8")))
        rows = cursor.fetchall()
        for row in rows:
            ret.append(row[0])
        cursor.execute('SELECT rid,rname from roominfo where rname=?',(rname.decode("utf8"),))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            if (row[0] in arooms) and (row[0] not in ret):
                ret.append(row[0])   
    else:
        ret = arooms    
    
    return (ret,arooms,brooms)

def getAreaRooms(area,exp_depth=2):
    arooms = []
    brooms = []
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT t2.rid  FROM area_name_map t1,(select rid,rname,ifnull(t_area,area) as tarea from v_traversal_roominfo) t2 where t1.area=t2.tarea and t1.cname=?',(area.decode("utf8"),))
    rows = cursor.fetchall()
    for row in rows:
        arooms.append(row[0])
    cursor.execute('SELECT t2.rid  FROM area_name_map t1,(select rid,rname,ifnull(t_area,area) as tarea from v_traversal_roominfo) t2,v_roomrel_nextarea t3 where t2.rid=t3.rid and t1.area=t2.tarea and t3.next_area<>? and t1.cname=?',(area.decode("utf8"),area.decode("utf8")))
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
    
def main(args):
    loc = args[1].decode("gb18030").encode("utf8");
    if len(args)==1:
        depth = 3
    else:
        depth = int(args[2].decode("gb18030").encode("utf8"));
#    loc='扬州打铁铺'
#    depth=2
    
    (area,rname) = loc_split(loc)
    
    (ridlist,arooms,brooms) = get_room_list(area,rname)
    
    #test:
#    print area,rname
#    print ridlist
    #####
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
