# -*- coding: utf-8 -*-
import sys
import re
import pdb
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

def main(args):
    #pdb.set_trace()
    #rid = "testrid"
    rid = args[1].decode("gb18030");
    #lines = "|||                 小校场    三清殿    小校场    |||                        ＼   ｜   ／|||                 小校场---武当广场---小校场    |||                      ／   ↑   ＼|||                 小校场    凌霄宫    小校场    ||||||武当广场 - [门派]||||||    这是一个由大石板铺成的广场，是武当弟子学习武功和互|||相切磋的地点。周围种满了梧桐树，一到秋天就是满地的落叶。|||一个年纪轻轻的道童正在打扫。北边是灵霄宫三清殿。|||  「深秋」: 东方的天空渐渐的发白了，又一个万物初醒的早上！。||||||    这里明显的出口是 north、east、southeast、northeast、west、southdown、southwest|||、northwest 和 eastdown。||||||    二位武当派小道士 道童(Daotong)|||    武当派真人 冲虚道长(Chongxu daozhang)|||>".split("|||")
    
    lines = args[2].decode("gb18030").encode("utf8").split("|||")     
    p = re.compile(r"^\s*((一|二|三|四|五|六|七|八|九|十)(位|只))?(.*?)\((.*?)\)( <(.*?)>)?$")
    conn = sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from room_npc where rid=?',(rid,)) 
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
#            print(npc_num)
#            print(npc_title1.decode("utf8").encode("gb18030"))
#            print(npc_title2.decode("utf8").encode("gb18030"))
#            print(npc_title3.decode("utf8").encode("gb18030"))
#            print(npc_cname.decode("utf8").encode("gb18030"))
#            print(npc_ename.decode("utf8").encode("gb18030"))
#            print(npc_status.decode("utf8").encode("gb18030"))
            cursor.execute('insert into room_npc (rid,npc_num,npc_title1,npc_title2,npc_title3,npc_cname,npc_ename) values (?,?,?,?,?,?,?)',(rid,npc_num,npc_title1.decode("utf8"),npc_title2.decode("utf8"),npc_title3.decode("utf8"),npc_cname.decode("utf8"),npc_ename.decode("utf8")));
            conn.commit()
    conn.close()
            
                
if __name__=="__main__":
    main(sys.argv)