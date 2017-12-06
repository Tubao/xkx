# -*- coding: utf-8 -*-
import sys
import re
from mydb import getconn

def main(args):
   
       #lines = "|||                            后堂               |||                             ｜     |||                 左配殿----三清殿----右配殿    |||                            ｜     |||                          武当广场             ||||||三清殿 - [门派]||||||    这里是凌霄宫的三清殿，是武当派会客的地点。供着元始|||天尊、太上道君和天上老君的神像，香案上香烟缭绕。靠墙放|||着几张太师椅，地上放着几个蒲团。东西两侧是走廊，南边是|||练武的广场，北边是后院。||||||    这里明显的出口是 north、south、east 和 west。||||||    神武功德录(Board) [ 115 张留言，115 张未读 ]|||   武当派道长 谷虚道长(Guxu daozhang)|||    武当派第三代弟子 中年道长(Zhongnian daozhang)|||    一流高手 武当派真人「武当首侠」宋远桥(Songyuanqiao)|||>".split("|||")
    lines = args[1].decode("gb18030").encode("utf8").split("|||");
    #lines = "|||                           星宿海              |||                             ｜     |||                           星宿海              |||                            ↓     |||                            湖泊               ||||||星宿海 - ||||||    这里是星宿海边。说是海，其实是片湖泊和沼泽，地形十分险恶。|||东面石壁上一道裂缝通到一个山洞。|||    「初春」: 太阳无奈地缓缓挂向西边的才露新芽的树梢。||||||    这里明显的出口是north 和 southup。||||||    垂头菊(Flower)|||    星宿派鼓手(Gushou)|||    星宿派号手(Haoshou)|||    钹手首领(Boshou shouling)|||   星宿派邪士「星宿派大师兄」摘星子(Zhaixing zi)|||    星宿派钹手(Boshou)|||> ".split("|||")
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
    cursor.execute('select rid,exitsdesc,area from roominfo where rname=? and rdesc=?',(roomname.decode("utf8"),roomdesc.decode("utf8")))
    rows = cursor.fetchall()
    conn.close()
    if len(rows)>0:
        for row in rows:           
            elist = p.split(row[1].encode("utf8"))
            elist.sort()            
            if sorteddesc == ','.join(elist):
                print row[2]
                print row[0]

       
if __name__=="__main__":
    main(sys.argv)
