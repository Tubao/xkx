import sqlite3

def getconn():
    return sqlite3.connect('/home/xiedw/git/xkx/pkuxkx/py/xkxmap.sqlite')
#    return sqlite3.connect('./xkxmap.sqlite')
