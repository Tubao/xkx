# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,MyNode,bfs
import Queue

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


def main(args):
    rid = args[1].decode("gb18030").encode("utf8");
    if len(args)==1:
        depth = 3
    else:
        depth = int(args[2].decode("gb18030").encode("utf8"));
    
    #points traversal:
            
    nodes = []
    
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
