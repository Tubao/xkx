# -*- coding: utf-8 -*-
import sys
from pathlib import Path
def main(args):    
    try:
        line = args[1].decode("gb18030")
    except Exception as e:
        return
    p = Path.cwd()    
    filename = "outputs.txt"
    f = p/filename
    with f.open('a',encoding = 'utf8') as file_handle:   # .txt可以不自己新建,代码会自动新建
        file_handle.write(line)     # 写入        
        return 1

if __name__=="__main__":
    main(sys.argv)
