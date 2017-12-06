# -*- coding: utf-8 -*-
import sys
import re
import pdb
def main(args):
    #pdb.set_trace()
    lines = args[1].decode("gb18030").encode("utf8").split("|||")
    for line in lines:        
        if re.search(r"^(\S+)",line):
            s = re.search(r"^(\S+)",line)            
            ss = s.group(1)
            print(ss.decode("utf8").encode("gb18030"))
            break
                
if __name__=="__main__":
    main(sys.argv)