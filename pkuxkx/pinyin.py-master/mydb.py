import sqlite3

def getconn():
#    return sqlite3.connect('./tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
    return sqlite3.connect('/home/xdw/tintin/myscripts/pkuxkx/gps/xkxmap.sqlite')
