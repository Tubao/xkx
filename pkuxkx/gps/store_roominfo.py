# -*- coding: utf-8 -*-
import sys
import re
import pdb
import hashlib
import sqlite3

def to_numbers(ch):
    n_dict = {"一":1,\
              "二":2,\
              "三":3,\
              "四":4,\
              "五":5,\
              "六":6,\
              "七":7,\
              "八":8,\
              "九":9,\
              "十":10}
    return n_dict[ch]

def md5digest(s):    
    hash_md5 = hashlib.md5(s)
    return hash_md5.hexdigest()

def main(args):
    #pdb.set_trace()
    bakid_check = str(args[3].decode("gb18030").encode("utf8"))
    #lines1 = "yz|||s|e|w|s|||n|e|w|n|||2|||-3|||-1".split("|||")
    lines1 = args[1].decode("gb18030").encode("utf8").split("|||")
    #$area|||$fromct|||$toct|||$xofct|||$yofct|||$zofct
    area = lines1[0]
    fromct = lines1[1]
    toct = lines1[2]
    xofct = lines1[3]
    yofct = lines1[4]
    zofct = lines1[5]
    #roomname:
    #lines = "|||                 小校场    三清殿    小校场    |||                        ＼   ｜   ／|||                 小校场---武当广场---小校场    |||                      ／   ↑   ＼|||                 小校场    凌霄宫    小校场    ||||||武当广场 - [门派]||||||    这是一个由大石板铺成的广场，是武当弟子学习武功和互|||相切磋的地点。周围种满了梧桐树，一到秋天就是满地的落叶。|||一个年纪轻轻的道童正在打扫。北边是灵霄宫三清殿。|||  「深秋」: 东方的天空渐渐的发白了，又一个万物初醒的早上！。||||||    这里明显的出口是 north、east、southeast、northeast、west、southdown、southwest|||、northwest 和 eastdown。||||||    二位武当派小道士 道童(Daotong)|||    武当派真人 冲虚道长(Chongxu daozhang)|||>".split("|||")
    #lines = "|||                            后堂               |||                             ｜     |||                 左配殿----三清殿----右配殿    |||                            ｜     |||                          武当广场             ||||||三清殿 - [门派]||||||    这里是凌霄宫的三清殿，是武当派会客的地点。供着元始|||天尊、太上道君和天上老君的神像，香案上香烟缭绕。靠墙放|||着几张太师椅，地上放着几个蒲团。东西两侧是走廊，南边是|||练武的广场，北边是后院。||||||    这里明显的出口是 north、south、east 和 west。||||||    神武功德录(Board) [ 115 张留言，115 张未读 ]|||   武当派道长 谷虚道长(Guxu daozhang)|||    武当派第三代弟子 中年道长(Zhongnian daozhang)|||    一流高手 武当派真人「武当首侠」宋远桥(Songyuanqiao)|||>".split("|||")
    
    lines = args[2].decode("gb18030").encode("utf8").split("|||")   
    roomname = ""
    roomdesc = ""
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
    
        #npcs
    p = re.compile(r"^\s*((一|二|三|四|五|六|七|八|九|十)(位|只))?(.*?)\((.*?)\)( <(.*?)>)?$")
    npclist = []
    for line in lines:
        if p.match(line):
            s = p.match(line)
            npc_num = 1
            if s.group(2) is not None:
                npc_num = to_numbers(s.group(2))
            ps = re.compile(r" |「|」")
            mylist = ps.split(s.group(4).strip(" "))
            npc_title1=""
            npc_title2=""
            npc_title3=""
            npc_cname=""
            ts = []
            for t in mylist:
                if t=="":
                    continue
                ts.append(t)
            if len(ts) == 4:
                npc_title1 = ts[0]
                npc_title2 = ts[1]
                npc_title3 = ts[2]
                npc_cname = ts[3]
            if len(ts) == 3:
                npc_title1 = ts[0]
                npc_title2 = ts[1]                
                npc_cname = ts[2]
            if len(ts) == 2:
                npc_title1 = ts[0]                             
                npc_cname = ts[1]
            if len(ts) == 1:                           
                npc_cname = ts[0]
            
            npc_ename = s.group(5)
            npc_status = s.group(7)
            if npc_status is None:
                npc_status = "normal"
            npcdict = {}
            npcdict["num"] = npc_num
            npcdict["title1"]=npc_title1
            npcdict["title2"]=npc_title2
            npcdict["title3"]=npc_title3
            npcdict["cname"]=npc_cname
            npcdict["ename"]=npc_ename
            npclist.append(npcdict)
     
#    print roomname
#    print roomdesc
#    print exitsdesc
#    print npclist[1]['cname']
    s = area + roomname + roomdesc + exitsdesc + str(xofct) + str(yofct) + str(zofct)
    rid = md5digest(s)
    s1 = area + roomname + roomdesc + exitsdesc
    bakid = md5digest(s1)
    
    #print rid
             
    conn = sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('select 1 from roominfo where bakid=?',(bakid,))
    row = cursor.fetchone()
    if row==None or bakid_check=="0":
        cursor.execute('select 1 from roominfo where rid=?',(rid,))
        row = cursor.fetchone()
        if row==None:
            cursor.execute('insert into roominfo (rid,area,fromct,toct,xofct,yofct,zofct, rname,rdesc,exitsdesc,bakid) values (?,?,?,?,?,?,?,?,?,?,?)',(rid,area.decode("utf8"),fromct,toct,xofct,yofct,zofct, roomname.decode("utf8"),roomdesc.decode("utf8"),exitsdesc.decode("utf8"),bakid));
            conn.commit()            
        print rid
    else:
        print 0
    conn.close()
       
if __name__=="__main__":
    main(sys.argv)
