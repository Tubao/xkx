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
   
    lines = args[1].decode("gb18030").encode("utf8").split("|||")
    area = args[2].decode("gb18030").encode("utf8")
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
    p = re.compile(r"、| 和 ")
    elist = p.split(exitsdesc)
    elist.sort()
    exitsdesc = ','.join(elist)
    
        
    s1 = area + roomname + roomdesc + exitsdesc
    bakid = md5digest(s1)
    print bakid
    
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rid from roominfo where bakid=?',(bakid,))
    row = cursor.fetchone()
    conn.close()
    if row==None:
        print 0
    else:
        print row[0]
       
if __name__=="__main__":
    main(sys.argv)
