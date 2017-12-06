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
    conn = getconn()
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
    bakid = md5digest(s1)
    print bakid    
          
if __name__=="__main__":
    main(sys.argv)
