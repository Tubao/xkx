# -*- coding: utf-8 -*-
import sys
import re
import pdb
import random
import sqlite3
import util
from mydb import getconn

class SearchProblem:
  """
  This class outlines the structure of a search problem, but doesn't implement
  any of the methods (in object-oriented terminology: an abstract class).
  
  You do not need to change anything in this class, ever.
  """
  
  def getStartState(self):
     """
     Returns the start state for the search problem 
     """
     util.raiseNotDefined()
    
  def isGoalState(self, state):
     """
       state: Search state
    
     Returns True if and only if the state is a valid goal state
     """
     util.raiseNotDefined()

  def getSuccessors(self, state):
     """
       state: Search state
     
     For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
     """
     util.raiseNotDefined()

  def getCostOfActions(self, actions):
     """
      actions: A list of actions to take
 
     This method returns the total cost of a particular sequence of actions.  The sequence must
     be composed of legal moves
     """
     util.raiseNotDefined()
           


class MyNode:
    def __init__(self,status,parent,actionFromParent,costFromParent):
        self.status = status
        self.parent = parent
        self.actionFromParent = actionFromParent
        self.costFromParent = costFromParent
        self.depthFromParent = 1
        self.priority = 0
    def getActions(self):
        a = []
        if self.parent is not None:
            a.extend(self.parent.getActions())
            a.append(self.actionFromParent)
        return a
    def getCost(self):
        c = 0
        if self.parent is not None:
            c = self.parent.getCost() + self.costFromParent
        return c
    def getDepth(self):
        c = 0
        if self.parent is not None:
            c = self.parent.getDepth() + self.depthFromParent
        return c
    def setPriority(self,p):
        self.priority = p
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
    def getNodes(self):
        n = []
        if self.parent is not None:
            n.extend(self.parent.getNodes())
        n.append(self)
        return n
      
import Queue
def depthFirstSearch(problem):        
    frontier = Queue.LifoQueue()
    explored = []    
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return None
        node = frontier.get()
        if problem.isGoalState(node.status):
            return (node.getActions(),node.getCost(),node.getNodes())
        explored.append(node)
        for successor in problem.getSuccessors(node.status):
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

def breadthFirstSearch(problem): 
    frontier = Queue.Queue()
    explored = []    
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return None
        node = frontier.get()
        if problem.isGoalState(node.status):
            return (node.getActions(),node.getCost(),node.getNodes())
        explored.append(node)
        for successor in problem.getSuccessors(node.status):
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
      
def uniformCostSearch(problem):
    frontier = Queue.PriorityQueue()
    explored = []    
    frontier.put(MyNode(problem.getStartState(),None,None,0))
    while True:
        if frontier.empty():
            return None
        node = frontier.get()
        if problem.isGoalState(node.status):
            return (node.getActions(),node.getCost(),node.getNodes())
        explored.append(node)
        for successor in problem.getSuccessors(node.status):
            s_status = successor[0]
            s_d = successor[1]
            s_c = successor[2]
            flag = True
            for n in frontier.queue:
                if n.status == s_status:
                    if n.getCost()>node.getCost()+s_c:
                        n.parent = node
                        n.actionFromParent = s_d
                        n.costFromParent = s_c
                        n.setPriority(n.getCost())
                    flag = False
            for n in explored:
                if n.status == s_status:
                    flag = False
            if flag:
                mn = MyNode(s_status,node,s_d,s_c)
                mn.setPriority(mn.getCost())
                frontier.put(mn)
    

def nullHeuristic(state, problem=None):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0

def mhdHeuristic(state, problem=None):
    goal_rid = problem.goal
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select xofct,yofct,zofct from roominfo where rid=?',(state,))
    row = cursor.fetchone()
    s_xofct = row[0]
    s_yofct = row[1]
    s_zofct = row[2]
    cursor.execute('select xofct,yofct,zofct from roominfo where rid=?',(goal_rid,))
    row = cursor.fetchone()
    g_xofct = row[0]
    g_yofct = row[1]
    g_zofct = row[2]
    conn.close()
    return abs(s_xofct-g_xofct) + abs(s_yofct-g_yofct) + abs(s_zofct-g_zofct)

def aStarSearch(problem, heuristic=nullHeuristic):
    proc = heuristic
    if type(proc) is str:
      proc = globals()[heuristic]
    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    frontier = Queue.PriorityQueue()
    explored = []    
    rn = MyNode(problem.getStartState(),None,None,0)
    rn.setPriority(rn.getCost() + proc(rn.status,problem))
    frontier.put(rn)
    while True:
        if frontier.empty():
            return None
        node = frontier.get()
        if problem.isGoalState(node.status):
            return (node.getActions(),node.getCost(),node.getNodes())
        explored.append(node)
        for successor in problem.getSuccessors(node.status):
            s_status = successor[0]
            s_d = successor[1]
            s_c = successor[2]
            flag = True
            for n in frontier.queue:
                if n.status == s_status:
                    if n.getCost()>node.getCost()+s_c:
                        n.parent = node
                        n.actionFromParent = s_d
                        n.costFromParent = s_c
                        n.setPriority(n.getCost() + proc(n.status,problem))
                    flag = False
            for n in explored:
                if n.status == s_status:
                    flag = False
            if flag:
                mn = MyNode(s_status,node,s_d,s_c)
                mn.setPriority(mn.getCost() + proc(mn.status,problem))
                frontier.put(mn)
    

    
  
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
def getaction(sexit,sbak1,sbak2):
    cmds = ""
    if sbak1 is None:
        cmds = sexit
    if sbak1 == "cmd":
        cmds = sbak2 + ";busy2;" + sexit
    if sbak1 == "kmove":
        cmds = "kmove " + sbak2 + " " + sexit + ";stop"
    if sbak1 == "busy":
        cmds = sexit + ";busy2"
    return cmds
def replaceWithTCCmd(sexit):    
    rdict = {"down":"gd",
             "up":"gup",
             "east":"ge",
             "north":"gn",
             "northeast":"gne",
             "northwest":"gnw",
             "south":"gs",
             "southeast":"gse",
             "southwest":"gsw",
             "west":"gw",
             "northup":"gnu",
             "southdown":"gsd",
             "northdown":"gnd",
             "southup":"gsu",
             "westup":"gwu",
             "eastdown":"ged",
             "westdown":"gwd",
             "eastup":"geu",
             "enter":"genter",
             "out":"gout"             
             }
    elist = sexit.split(";")
    ret = ""
    for e in elist:
        te = e
        try:
            te = rdict[e]
        except KeyError:
            te = e
        ret = ret + te + ";"
    return ret[:-1]
def getTCaction(sexit,sbak1,sbak2):
    cmds = ""
    if sexit<>"":
        sexit = replaceWithTCCmd(sexit)
    if sbak1 is None:
        cmds = sexit
    if sbak1 == "cmd":
        cmds = sbak2 + ";busy2;" + sexit
    if sbak1 == "kmove":
        cmds = "kmove " + sbak2 + " " + sexit + ";stop"
    if sbak1 == "busy":
        cmds = sexit
    return cmds        
class MudRoomSearchProblem(SearchProblem):
  """
  A search problem defines the state space, start state, goal test,
  successor function and cost function.  This search problem can be 
  used to find paths between mud game rooms.
  
  The state space consists of rid for room.
  
  """
  
  def __init__(self, init_rid, goal, costFn = lambda x: 1, start=None):
    """
    Stores the start and goal.  
    
    init_rid:init room id
    costFn: A function from a search state to a non-negative number
    goal: rid of destination
    """
    self.startState = init_rid    
    self.goal = goal
    self.costFn = costFn
    
  def getStartState(self):
    return self.startState

  def isGoalState(self, state):
     isGoal = state == self.goal         
     return isGoal   
   
  def getSuccessors(self, state):
    """
    Returns successor states, the actions they require, and a cost of 1.
    
     As noted in search.py:
         For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
    """
    
    successors = []
    #get from roomrel table
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid,nextrid,exit,bak1,bak2,cost from roomrel where rid=?',(state,))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        nextState = row[1]
        action = getaction(row[2],row[3],row[4])
        if row[5] is None or row[5]=="":
            cost = 1
        else:
            cost = int(row[5])
        successors.append( ( nextState, action, cost) )
                
    return successors
    
  def getTraversalSuccessors(self, state):
    """
    Returns successor states, the actions they require, and a cost of 1.
    
     As noted in search.py:
         For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
    """
    
    successors = []
    #get from roomrel table
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid,nextrid,exit,bak1,bak2,cost from roomrel where flag=0 and rid=?',(state,))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        nextState = row[1]
        action = getaction(row[2],row[3],row[4])
        if row[5] is None or row[5]=="":
            cost = 1
        else:
            cost = int(row[5])
        successors.append( ( nextState, action, cost) )
                
    return successors    

  def getTCSuccessors(self, state):
    """
    Returns successor states, the actions they require, and a cost of 1.
    
     As noted in search.py:
         For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
    """
    
    successors = []
    #get from roomrel table
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid,nextrid,exit,bak1,bak2,cost from roomrel where rel_type="normal" and rid=?',(state,))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        nextState = row[1]
        action = getTCaction(row[2],row[3],row[4])
        if row[5] is None or row[5]=="":
            cost = 1
        else:
            cost = int(row[5])
        successors.append( ( nextState, action, cost) )
                
    return successors

  def getCostOfActions(self, actions):
    """
    Returns the cost of a particular sequence of actions. 
    """
    
    return len(actions)

    
def depthFirstTraversal(problem,depth = 3):        
    frontier = Queue.LifoQueue()
    explored = []    
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
def breadthFirstTraversal(problem,depth=3): 
    frontier = Queue.Queue()
    explored = []    
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
                
dft = depthFirstTraversal
bft = breadthFirstTraversal
               
def getroomname(rid):
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rname from roominfo where rid=?',(rid,))
    row = cursor.fetchone()
    conn.close()
    return row[0]

def lbylines(ref_rid,lines):
    roomname=""
    roomdesc=""
    step = 0
    for i,line in enumerate(lines):
        if step==0 and re.search(r"^(\S.*?) -",line):
            s = re.search(r"^(\S.*?) -",line)            
            ss = s.group(1)
            roomname = ss
            step = 2
            continue
        if step == 2 and len(line.strip())==0:            
            continue
        if step == 2 and len(line.strip())>0:
            roomdesc = roomdesc + line
            step = 3
            continue
        if step == 3 and re.search(r"^一片浓雾中，什么也看不清。",line):
            break
        if step == 3 and re.search(r"^\S+",line):
            roomdesc = roomdesc + line
            continue
        if step == 3 and re.search(r"^\s+",line):
           break
       
    startline = 0
    myline = ""
    for line in lines:        
        if re.search(r"^\s*这里.*?的.*?有 ",line):
            startline = 1
            myline = line
            if re.search(r"。$",line):
                startline = 0
                break
            else:
                continue
        if startline == 1:
            myline = myline + line
            if re.search(r"。$",line):
                startline = 0
                break
            else:
                continue
        
    s = re.search(r"^\s*这里.*?的.*?有 (.*?)。",myline)
    exitsdesc = ""
    if len(myline)>0:
        exitsdesc = s.group(1)
    p = re.compile(r"、| 和 ")
    elist = p.split(exitsdesc)
    elist.sort()
    sorteddesc = ','.join(elist)
    
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid,exitsdesc from roominfo where rname=? and rdesc=?',(roomname.decode("utf8"),roomdesc.decode("utf8")))
    rows = cursor.fetchall()
    conn.close()
    myrids = []
    ridcount=0
    if len(rows)==0:
        return 0    
    else:
        for row in rows:           
            elist = p.split(row[1].encode("utf8"))
            elist.sort()            
            if sorteddesc == ','.join(elist):
                myrids.append(row[0])
                ridcount = ridcount + 1
        if ridcount==1:
            return myrids[0]
        if ridcount==0:
            return 0
        if ridcount>1:       
            k = 0
            v = 99999
            for myrid in myrids:
                c_rid = myrid
                if c_rid == ref_rid:
                    return ref_rid
                else:
                    p = MudRoomSearchProblem(ref_rid,c_rid)
                    _,cost,_ = bfs(p)
                    if v > cost:
                        k = c_rid
                        v = cost
            return k
def lbylines2(lines):
    roomname=""
    roomdesc=""
    step = 0
    for i,line in enumerate(lines):
        if step==0 and re.search(r"^(\S.*?) -",line):
            s = re.search(r"^(\S.*?) -",line)
            ss = s.group(1)
            roomname = ss
            step = 2
            continue
        if step == 2 and len(line.strip())==0:            
            continue
        if step == 2 and len(line.strip())>0:
            roomdesc = roomdesc + line
            step = 3
            continue
        if step == 3 and re.search(r"^一片浓雾中，什么也看不清。",line):
            break
        if step == 3 and re.search(r"^\S+",line):
            roomdesc = roomdesc + line
            continue
        if step == 3 and re.search(r"^\s+",line):
           break
       
    startline = 0
    myline = ""
    for line in lines:        
        if re.search(r"^\s*这里.*?的.*?有 ",line):
            startline = 1
            myline = line
            if re.search(r"。$",line):
                startline = 0
                break
            else:
                continue
        if startline == 1:
            myline = myline + line
            if re.search(r"。$",line):
                startline = 0
                break
            else:
                continue
        
    s = re.search(r"^\s*这里.*?的.*?有 (.*?)。",myline)
    exitsdesc = ""
    if len(myline)>0:
        exitsdesc = s.group(1)
    p = re.compile(r"、| 和 ")
    elist = p.split(exitsdesc)
    elist.sort()
    sorteddesc = ','.join(elist)
    
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid,exitsdesc from roominfo where rname=? and rdesc=?',(roomname.decode("utf8"),roomdesc.decode("utf8")))
    rows = cursor.fetchall()
    conn.close()
    myrid = "0"
    ridcount=0
    if len(rows)==0:
        return (0,0)
    else:
        for row in rows:           
            elist = p.split(row[1].encode("utf8"))
            elist.sort()            
            if sorteddesc == ','.join(elist):
                myrid = row[0]
                ridcount = ridcount + 1
        if ridcount==1:
            return (1,myrid)
        if ridcount==0:
            return (0,0)
        if ridcount>1:            
            return (2,ridcount)
            
def getExits(lines):
    startline = 0
    myline = ""
    for line in lines:        
        if re.search(r"^\s*这里.*?的.*?有 ",line):
            startline = 1
            myline = line
            continue
        if startline == 1 and re.search(r"^\S+",line):
            myline = myline + line
            continue
        if startline == 1 and re.search(r"^\s+",line):
            startline = 0
            break
        
    s = re.search(r"^\s*这里.*?的.*?有 (.*?)。",myline)
    ss = s.group(1)
    p = re.compile(r"、| 和 ")
    ret = p.split(ss)
    random.shuffle(ret)
    return ret
    

        
def main(args):
    
#    init_rid = 'a4437744fdf7f0424661135d1ec16806'
#    goal_rid = 'f2cfcf9527481ed03ffac37a7ce45c37'
#    p = MudRoomSearchProblem(init_rid,goal_rid)
#    actions,cost,nodes = bfs(p)
#    ret = ""
#    for act in actions:
#        ret = ret + act + ";"
#    print ret
#    
    lines = "|||                                               |||                                    |||                           问津亭----草地      |||                            ｜     |||                           日月洞              ||||||问津亭 - ||||||    这是一座六角形的亭台，古意妙趣横生。坐在亭中，微风吹过，心旷神怡。|||    「隆冬」: 夜幕笼罩著大地，万物在洁白的厚雪下沉沉睡去。||||||    这里明显的方向有 east 和 south。||||||>".split("|||")
    (ltype,content) = lbylines2(lines)    
    print ltype
    print content
    
#    
#    print actions[0]
#
#    print getroomname(nodes[1].status)
#    
#    print cost
#    
#    nodes = dft(p,3)
#    print [n.status for n in nodes]
#
#    nodes.append(nodes[0])
#    i = 0
#    while i<len(nodes)-1:
#        init_rid = nodes[i].status
#        goal_rid = nodes[i+1].status
#        p = MudRoomSearchProblem(init_rid,goal_rid)
#        actions,_,_=bfs(p)
#        ret = ""
#        for act in actions:
#            ret = ret + act + ";"
#        print getroomname(nodes[i].status) + " to " + getroomname(nodes[i+1].status) + " : " + ret
#        i = i + 1



#       ref_rid =  '3580b73e330da2fb4898ced1fe3e282f'
#       lines = "|||                            后堂               |||                             ｜     |||                 左配殿----三清殿----右配殿    |||                            ｜     |||                          武当广场             ||||||三清殿 - [门派]||||||    这里是凌霄宫的三清殿，是武当派会客的地点。供着元始|||天尊、太上道君和天上老君的神像，香案上香烟缭绕。靠墙放|||着几张太师椅，地上放着几个蒲团。东西两侧是走廊，南边是|||练武的广场，北边是后院。||||||    这里明显的出口是 north、south、east 和 west。||||||    神武功德录(Board) [ 115 张留言，115 张未读 ]|||   武当派道长 谷虚道长(Guxu daozhang)|||    武当派第三代弟子 中年道长(Zhongnian daozhang)|||    一流高手 武当派真人「武当首侠」宋远桥(Songyuanqiao)|||>".split("|||")
#       goal_rid = '293a60e53f92c57ae29e44e4a3621064'
#       print lbylines(ref_rid,lines)
#       print getroomname(locatebylines(ref_rid,lines))
#       print getExits(lines)
#       print walk_stepbystep(ref_rid,lines,goal_rid)
       
if __name__=="__main__":
    main(sys.argv)
