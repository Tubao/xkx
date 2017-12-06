# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem,bfs,ucs

def main(args):
    #2d5c8daa1b737d97509231fda8c49d05 9834ec789ab9f8f08c46c50678f66f3a
    init_rid = args[1].decode("gb18030");
    goal_rid = args[2].decode("gb18030");
#    init_rid = '2d5c8daa1b737d97509231fda8c49d05'
#    goal_rid = '9834ec789ab9f8f08c46c50678f66f3a'
    p = MudRoomSearchProblem(init_rid,goal_rid)
    actions,cost,nodes = ucs(p)
    ret = str(cost) + ";"
    for act in actions:
        ret = ret + act + ";"
    
    retlist = ret.split(";")
    for a in retlist:
        print a

       
if __name__=="__main__":
    main(sys.argv)
