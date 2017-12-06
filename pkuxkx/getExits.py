# -*- coding: utf-8 -*-
import sys
import re
import pdb
import random
def main(args):
    #pdb.set_trace()
    #lines = "|||                 小校场    三清殿    小校场    |||                        ＼   ｜   ／|||                 小校场---武当广场---小校场    |||                      ／   ↑   ＼|||                 小校场    凌霄宫    小校场    ||||||武当广场 - [门派]||||||    这是一个由大石板铺成的广场，是武当弟子学习武功和互|||相切磋的地点。周围种满了梧桐树，一到秋天就是满地的落叶。|||一个年纪轻轻的道童正在打扫。北边是灵霄宫三清殿。|||  「深秋」: 东方的天空渐渐的发白了，又一个万物初醒的早上！。||||||    这里明显的出口是 north、east、southeast、northeast、west、southdown、southwest|||、northwest 和 eastdown。||||||    二位武当派小道士 道童(Daotong)|||    武当派真人 冲虚道长(Chongxu daozhang)|||>".split("|||")
    #lines = "|||                            后堂               |||                             ｜     |||                 左配殿----三清殿----右配殿    |||                            ｜     |||                          武当广场             ||||||三清殿 - [门派]||||||    这里是凌霄宫的三清殿，是武当派会客的地点。供着元始|||天尊、太上道君和天上老君的神像，香案上香烟缭绕。靠墙放|||着几张太师椅，地上放着几个蒲团。东西两侧是走廊，南边是|||练武的广场，北边是后院。||||||    这里明显的出口是 north、south、east 和 west。||||||    神武功德录(Board) [ 115 张留言，115 张未读 ]|||   武当派道长 谷虚道长(Guxu daozhang)|||    武当派第三代弟子 中年道长(Zhongnian daozhang)|||    一流高手 武当派真人「武当首侠」宋远桥(Songyuanqiao)|||>".split("|||")
    lines = args[1].decode("gb18030").encode("utf8").split("|||")
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
    ss = s.group(1)
    p = re.compile(r"、| 和 ")
    ret = p.split(ss)
    random.shuffle(ret)
    for r in ret:
        print(r)
                
if __name__=="__main__":
    main(sys.argv)