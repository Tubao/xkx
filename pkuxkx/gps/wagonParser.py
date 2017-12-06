# -*- coding: utf-8 -*-
import sys
import pdb
import re
from mydb import getconn
import sqlite3   
    
def main(args):   
    #hereid = args[1].decode("gb18030")
    hereid = "0d89a7078030d6f2efbfb91617528c0b"
    wfile = open("wagon.txt")
    lines = wfile.readlines()
    
    ##pdb.set_trace()
    rr = re.compile(r"^\s*\d+\s*(\W+?)\s*([a-z]+)\s+.*".decode("utf8"))
    #conn = getconn()
    conn = sqlite3.connect('./xkxmap.sqlite')
    cursor = conn.cursor()
    for line in lines:
        if rr.search(line.decode("gb18030")):
            s = rr.search(line.decode("gb18030"))
            ss = s.group(1)    
            py = s.group(2)
            print ss,py
            sqlstr = "select rid from roominfo t1,area_name_map t2 where  (t1.rname like '%马车%' or t1.rname like '%车行%'  or t1.rname like '%大车店%') and t1.area=t2.area and t2.cname=?".decode("utf8")
            cursor.execute(sqlstr,(ss,))
            row = cursor.fetchone()
            nextrid = row[0]
            print nextrid
            cmdstr = "gu;qu " + py + ";stop"
            cursor.execute("insert into roomrel (rid,nextrid,exit,cost,flag,rel_type) values(?,?,?,?,?,?)",(hereid,nextrid,cmdstr,100,1,'wagon'))
            conn.commit()
    conn.close()
           
       
       
if __name__=="__main__":
    main(sys.argv)
