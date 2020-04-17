# -*- coding: utf-8 -*-
import sys
from pathlib import Path
def main(args):
    last_cmd_index = int(args[1])
    #last_mtime = 0
    p = Path.cwd()   
    p = p/"cmd_files"
    if not p.exists(): 
        print "-9"       
        return
    if last_cmd_index == -2:
        for file in p.glob('*'):
            file.unlink()
        print "-1"
        print "hi"
        return
    ret = []
    #check if event engine has reset index
    index_reset = False
    for file in p.glob('*'):
        if file.name[3:]=="88888888":
            index_reset = True
            file.unlink()
            last_cmd_index = -1
            break

    for file in p.glob('*'):        
        if not index_reset and int(file.name[3:])<=last_cmd_index:
            continue
        cmd_index = int(file.name[3:])        
        cmd = ""
        with file.open('r',encoding = 'utf8') as file_handle:   # .txt可以不自己新建,代码会自动新建
            cmd = file_handle.readline()    
        ret.append([cmd_index,cmd])
    if len(ret)==0:
        print "-9"        
        return
    ret = sorted(ret,key=lambda x:x[0])
    for r in ret:
        print r[0]
        print r[1]

if __name__=="__main__":
    main(sys.argv)
