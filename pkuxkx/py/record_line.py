# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from redisMQ import RedisMQ,Event
def main(args):
    filename = "mud_lines"
    if len(args)>2:
        filename = args[2]
    try:
        line = args[1].decode("gb18030")
    except Exception as e:
        return
    rmq= RedisMQ()        
    myevent = Event("line_event")
    myevent.dict_['data'] = line
    rmq.put(myevent) 

    
 
    """ 
        p = Path.cwd()    
        f = p/filename
        with f.open('a',encoding = 'utf8') as file_handle:   # .txt可以不自己新建,代码会自动新建
            file_handle.write(line)     # 写入
            file_handle.write('\n'.decode("utf-8"))         # 有时放在循环里面需要自动转行，不然会覆盖上一条数据
            #push line into mq:
            rmq= RedisMQ()        
            myevent = Event("line_event")
            myevent.dict_['data'] = line
            rmq.put(myevent)        
            return 1 """ 

if __name__=="__main__":
    main(sys.argv)
