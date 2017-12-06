# -*- coding: utf-8 -*-
import sys
import pdb
from mydb import getconn
import re
import hashlib

def md5digest(s):    
    hash_md5 = hashlib.md5(s)
    return hash_md5.hexdigest()
    
def main(args):
    rid = args[1].decode("gb18030")
    #rid = '6d9de40de944b975eb87f20bf0c9f0a1'
    lines = args[2].decode("gb18030").encode("utf8").split("|||")
    area = args[3].decode("gb18030").encode("utf8")
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
            continue
        if startline == 1 and re.search(r"^\S+",line):
            myline = myline + line
            continue
        if startline == 1 and re.search(r"^\s+",line):
            startline = 0
            break
        
    s = re.search(r"^\s*这里.*?的.*?有 (.*?)。",myline)
    exitsdesc = ""
    if len(myline)>0:
        exitsdesc = s.group(1)
    p = re.compile(r"、| 和 ")
    elist = p.split(exitsdesc)
    elist.sort()
    exitsdesc = ','.join(elist)
        
    s1 = area + roomname + roomdesc + exitsdesc
    bakid1 = md5digest(s1)
    
    conn = getconn()
    #conn = sqlite3.connect('./xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('select area,rname,rdesc,exitsdesc from roominfo where rid=?',(rid,))
    row = cursor.fetchone()
    area = row[0].encode("utf8")
    roomname = row[1].encode("utf8")
    roomdesc = row[2].encode("utf8")
    exitsdesc = row[3].encode("utf8")
    conn.close()
    
    p = re.compile(r"、| 和 ")
    elist = p.split(exitsdesc)
    elist.sort()
    exitsdesc = ','.join(elist)
    
        
    s1 = area + roomname + roomdesc + exitsdesc
    bakid2 = md5digest(s1)
    if bakid1<>bakid2:        
        print 0
    else:
        print 1
    
       
if __name__=="__main__":
    main(sys.argv)
