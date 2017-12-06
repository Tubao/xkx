# -*- coding: utf-8 -*-
import sys
import pdb
from mydb import getconn
import re
import hashlib
from pinyin import PinYin


def main(args):
   
    test = PinYin()
    test.load_word()
    
    conn = getconn()
    cursor = conn.cursor()
    cursor.execute('select rname,rid from roominfo where py_name is null')
#    cursor.execute('select cname,area from area_name_map where py_name is null')
    rows = cursor.fetchall()
    
    for row in rows:
        myword = row[0].encode("utf8")    
        pylist = test.hanzi2pinyin(string=myword)    
        pystr = pylist[0]
        for w in pylist[1:]:
            pystr = pystr + w[0]
#        cursor.execute('update area_name_map set py_name=? where cname=? and area=?',(pystr,row[0],row[1]))
        cursor.execute('update roominfo set py_name=? where rid=?',(pystr,row[1]))
        conn.commit()
    conn.close() 
#    conn = getconn()
#    cursor = conn.cursor()
#    cursor.execute('select rid from roominfo where bakid=?',(bakid,))
#    row = cursor.fetchone()
#    conn.close()
#    if row==None:
#        print 0
#    else:
#        print row[0]
       
if __name__=="__main__":
    main(sys.argv)
