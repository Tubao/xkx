# -*- coding: utf-8 -*-
import sys
from mydb import getconn

def main(args):
   
    rid = args[1].decode("gb18030")
    moves = args[2].decode("gb18030").encode("utf8").split("|||")
    
    conn = getconn()
    cursor = conn.cursor()
    for mymove in moves[:-1]:
        cursor.execute('select rid from roomrel where nextrid=? and exit=?',(rid,mymove.decode("utf8")))
        row = cursor.fetchone()
        if row is not None:
            rid = row[0]
    conn.close()    
    print rid.encode("gb18030")
    
       
if __name__=="__main__":
    main(sys.argv)
