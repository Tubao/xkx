# -*- coding: utf-8 -*-
import sys
import pdb
import sqlite3

def main(args):
    rid = args[1].decode("gb18030");
    nextrid = args[2].decode("gb18030");
    myexit = args[3].decode("gb18030");
    bexit = args[4].decode("gb18030");

    conn = sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('select 1 from roomrel where rid=? and nextrid=?',(rid,nextrid))
    row = cursor.fetchone()
    
    if row==None:       
        cursor.execute('insert into roomrel (rid,nextrid,exit,bexit) values(?,?,?,?)',(rid,nextrid,myexit,bexit))
        conn.commit()
        
    cursor.execute('select 1 from roomrel where rid=? and nextrid=?',(nextrid,rid))
    row = cursor.fetchone()
    
    if row==None:       
        cursor.execute('insert into roomrel (rid,nextrid,exit,bexit) values(?,?,?,?)',(nextrid,rid,bexit,myexit))
        conn.commit()
    conn.close()
    
       
if __name__=="__main__":
    main(sys.argv)
