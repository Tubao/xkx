# -*- coding: utf-8 -*-
import sys
from mudsearch import MudRoomSearchProblem
from getcmds_sbs import breadthFirstTCSearch
def walk_stepbystep2(ref_rid,goal_rid):
    #return action and next ref_rid
    if len(ref_rid)==0 or ref_rid == "0":
        return ("0","0")
    else:
        p = MudRoomSearchProblem(ref_rid,goal_rid)
        actions,cost,nodes = breadthFirstTCSearch(p)
        if len(actions)==0 or len(nodes)<1:
            return ("0","0")
        else:
            return (actions[0],nodes[1].status)

def main(args):
#    ref_rid =  '3580b73e330da2fb4898ced1fe3e282f'
#    lines = "|||                            后堂               |||                             ｜     |||                 左配殿----三清殿----右配殿    |||                            ｜     |||                          武当广场             ||||||三清殿 - [门派]||||||    这里是凌霄宫的三清殿，是武当派会客的地点。供着元始|||天尊、太上道君和天上老君的神像，香案上香烟缭绕。靠墙放|||着几张太师椅，地上放着几个蒲团。东西两侧是走廊，南边是|||练武的广场，北边是后院。||||||    这里明显的出口是 north、south、east 和 west。||||||    神武功德录(Board) [ 115 张留言，115 张未读 ]|||   武当派道长 谷虚道长(Guxu daozhang)|||    武当派第三代弟子 中年道长(Zhongnian daozhang)|||    一流高手 武当派真人「武当首侠」宋远桥(Songyuanqiao)|||>".split("|||")
#    goal_rid = '2d7e8c327742dfd1c95e24f963c47c2e'
#    print lbylines(ref_rid,lines)
#    print getroomname(locatebylines(ref_rid,lines))
#    print getExits(lines)
#    print walk_stepbystep(ref_rid,lines,goal_rid)

    #2d5c8daa1b737d97509231fda8c49d05 9834ec789ab9f8f08c46c50678f66f3a
    ref_rid = args[1].decode("gb18030").encode("utf8");    
    goal_rid = args[2].decode("gb18030").encode("utf8");
    (nextaction,nextrid) = walk_stepbystep2(ref_rid,goal_rid)
    print nextrid
    retlist = nextaction.split(";")
    for a in retlist:
        print a

       
if __name__=="__main__":
    main(sys.argv)
