# -*- coding: utf-8 -*-
import sys
import pdb
import sqlite3

def main(args):
    rid = args[1].decode("gb18030").encode("utf8")
    #rid = '6d9de40de944b975eb87f20bf0c9f0a1'
    conn = sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    #conn = sqlite3.connect('./xkxmap.sqlite')
    cursor = conn.cursor()
    cursor.execute('select rid,area,fromct,toct,xofct,yofct,zofct, rname,rdesc,exitsdesc from roominfo where rid=?',(rid,))
    row = cursor.fetchone()
    conn.close()
    if row==None:        
        print 0
    else:
        print row[0]
        print row[1].encode("gb18030")
        print row[2]
        print row[3]
        print row[4]
        print row[5]
        print row[6]
        print row[7].encode("gb18030")
        print row[8].encode("gb18030")
        print row[9].encode("gb18030")
    
       
if __name__=="__main__":
    main(sys.argv)
