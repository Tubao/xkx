# -*- coding: utf-8 -*-
import sys
import re
import pdb
def to_numbers(cns):
    n_dict = {"一":1,\
              "二":2,\
              "三":3,\
              "四":4,\
              "五":5,\
              "六":6,\
              "七":7,\
              "八":8,\
              "九":9,\
              "十":10,\
              "百":100,\
              "千":1000,\
              "万":10000,\
              "零":0}
    p = re.compile(r"零|一|二|三|四|五|六|七|八|九|十|百|千|万")
    cnlist = p.findall(cns)
    cnlist = cnlist[::-1]
    ret = 0
    multi = 1
    wflag = 0
    
    for cn in cnlist:
        n = n_dict[cn]
        if n==10000:
            wflag=1
        elif n<10:
            ret = ret + n*multi*pow(10000,wflag)
            multi = 1
        else:
            multi=n
    if multi>1:
        ret = ret + multi*pow(10000,wflag)
    return ret
    
    


def main(args):
    #pdb.set_trace()
    lines = args[1].decode("gb18030").encode("utf8").split("|||")   
    #lines = "|||┌──────────────────────────────────────────────────┐|||│        你身上带着五件东西         (负重  2%)：                                                    │|||├───────────────────────[装  备]───────────────────────┤|||│                                 -- [帽子]__   ███   __[副兵] --                                 │|||│                                -- [护面]__    o  o ☆ __[护腕] --                                 │|||│                                 --[披风]__   ▂﹀▂ ▌__[手套] --                                 │|||│                                 -- [护肩]__ ▅█Ψ  █ __[铠甲] --                               │|||│                    青色道袍   (+2) [衣服]__ ████▂ __[护肩] --                                 │|||│                                -- [腰带]__ ▌  ═     __[盾牌] --                                 │|||│                                 --[主兵]__ ★█禁█   __[护腿] --                                 │|||│                                 -- [护腿]__ ▄█  █▄ __[鞋子] 麻鞋  (+0)                        │|||├───────────────────────[饰  品]───────────────────────┤|||│ Ψ[项链]                   --                                      --                   [护心]·  │|||│  ★[戒指]                   --                                    --                   [戒指]☆  │|||├───────────────────────[其  它]───────────ぉぉぉぉぉぉぉぉぉぉぉぉ葇||│锦囊(Jin nang)                                    七十五两白银(Silver)                             │|||│三两黄金(Gold)                                                                                      │|||╰──────────────────────────────────────────────────╯|||> "
    #lines = lines.split("|||")
    prep = re.compile(r"[其  它]")
    p = re.compile(r"\S+\(.+?\)")     
    cnp = re.compile(r"^((零|一|二|三|四|五|六|七|八|九|十|百|千|万)*)(.*?)\((.+?)\)")
    start_flag = True
    for line in lines:
        line = line.replace("│","")        
        if  start_flag and prep.search(line):
            start_flag = False
            continue
        elif start_flag:
            continue
        else:
            mylist = p.findall(line)
            if len(mylist) == 0:
                continue
            for item in mylist:                
                s = cnp.match(item)
                num = 1
                if len(s.group(1))>0:
                    num = to_numbers(s.group(1))
                    cname = s.group(3)[3:]
                    ename = s.group(4)
                else:
                    cname = s.group(3)
                    ename = s.group(4)
            
                print(num)
                print(cname.decode("utf8").encode("gb18030"))                
                print(ename.lower().decode("utf8").encode("gb18030"))
            
if __name__=="__main__":
    main(sys.argv)    
    