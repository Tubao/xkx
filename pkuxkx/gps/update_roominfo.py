# -*- coding: utf-8 -*-
import sys
import re
import pdb
import hashlib
import sqlite3
from mydb import getconn

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
    
    #lines1 = "yz|||s|e|w|s|||n|e|w|n|||2|||-3|||-1".split("|||")
    old_rid = args[1].decode("gb18030")
#    old_rid="bc50074a9e9a76f0d6499aa0f992939e"
    #$area|||$fromct|||$toct|||$xofct|||$yofct|||$zofct
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select area,fromct,toct,xofct,yofct,zofct,t_area,py_name,room_type from roominfo where rid=?',(old_rid,))
#    print 'select area,fromct,toct,xofct,yofct,zofct,t_area,py_name,room_type from roominfo where rid={0}'.format(old_rid)
    row = cursor.fetchone()
    area = row[0].encode("utf8")
    fromct = row[1].encode("utf8")
    toct = row[2].encode("utf8")
    xofct = row[3]
    yofct = row[4]
    zofct = row[5]
    t_area = row[6]
    py_name = row[7]
    room_type = row[8]   
    #roomname:
#    lines = "||||||                                     黄河南岸  |||                                  ／|||                 大官道----虎牢关             |||                        ／        ＼|||               山野小径              官道      ||||||虎牢关 - ||||||    这里是洛阳东边门户和重要的关隘，因西周穆王在此牢虎而得名。其南连嵩|||岳，北濒黄河，山岭交错，自成天险。大有“一夫当关，万夫莫开”之势，为历|||代兵家必争之地。|||    「初春」:清晨，东方的天空布满了灰蒙蒙的云层。||||||    这里明显的方向有 southeast、southwest、west 和 northeast。||||||".split("|||")
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
#    print 'here begin md5'
    s = area + roomname + roomdesc + exitsdesc + str(xofct) + str(yofct) + str(zofct)
#    print s.decode('utf8').encode("gb18030")
    rid = md5digest(s)
#    print rid
    s1 = area + roomname + roomdesc + exitsdesc
    bakid = md5digest(s1)
#    
#    
#    
    cursor.execute('select 1 from roominfo where rid=?',(rid,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('delete from roominfo where rid=?',(old_rid,))
#        print 'delete from roominfo where rid={0}'.format(old_rid)
        cursor.execute('insert into roominfo (rid,area,fromct,toct,xofct,yofct,zofct, rname,rdesc,exitsdesc,bakid,t_area,py_name,room_type) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(rid,area.decode("utf8"),fromct.decode("utf8"),toct,xofct,yofct,zofct, roomname.decode("utf8"),roomdesc.decode("utf8"),exitsdesc.decode("utf8"),bakid,t_area,py_name,room_type))
#        print 'insert into roominfo (rid,area,fromct,toct,xofct,yofct,zofct, rname,rdesc,exitsdesc,bakid,t_area,py_name,room_type) values ({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13})'.format(rid,area.decode("utf8").encode("gb18030"),fromct.decode("utf8").encode("gb18030"),toct,xofct,yofct,zofct, roomname.decode("utf8").encode("gb18030"),roomdesc.decode("utf8").encode("gb18030"),exitsdesc.decode("utf8").encode("gb18030"),bakid,t_area,py_name,room_type)
        #update roomrel:
        cursor.execute('update roomrel set rid=? where rid=?',(rid,old_rid))
#        print 'update roomrel set rid={0} where rid={1}'.format(rid,old_rid)
        cursor.execute('update roomrel set nextrid=? where nextrid=?',(rid,old_rid))
#        print 'update roomrel set nextrid={0} where nextrid={1}'.format(rid,old_rid)
        conn.commit()        
        print rid
    else:
        print '0'
    
    conn.close()
       
if __name__=="__main__":
    main(sys.argv)
