# -*- coding: utf-8 -*-
import sys
import pdb
import sqlite3

def main(args):
    rid = args[1].decode("gb18030");
    conn = sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('select xofct from roominfo where rid=?',(rid,))
    row = cursor.fetchone()
    conn.close()
    if row==None:        
        print 0
    else:
        print row[0]
    
       
if __name__=="__main__":
    main(sys.argv)
