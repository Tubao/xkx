# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from redisMQ import RedisMQ,Event
from time import sleep
import re
from threading import Timer,Lock
import csv
import os
import json
from collections import defaultdict
import traceback
import pdb
import sys
import pygame
import cfg_gui
import math
import copy
from Queue import Queue
import hashlib
import networkx as nx
import matplotlib.pyplot as plt
from gui_tools import TextBox

reload(sys)
sys.setdefaultencoding('utf8')

myConfig = {"ticker":[],"current_tickers":[]}
lock = Lock()
global_cmdIndex = 0
cmd_queue = Queue(maxsize=10)
cache_resp = defaultdict(list)
CACHE_SIZE = 200

file_mtime_dict = defaultdict(float)
trigger_flags = defaultdict(int)
record_lines = defaultdict(list)

G = nx.DiGraph()
nodes_init_pos = {}
rid_room_dict = {}
rid_cname_dict = {}
min_map = None
############################################################################
#########             major classes           ################
#############################################################################
def md5digest(s):    
    hash_md5 = hashlib.md5(s)
    return hash_md5.hexdigest()

class MudItem(object):
    def __init__(self):
        self.ename = ""
        self.cname = ""
        self.type = "other"
        self.amount = 0
    def __str__(self):
        return self.type + ": " + str(self.amount) + " " + self.cname + " (" + self.ename + ")"
class MudNpc(object):
    def __init__(self):
        self.ename = ""
        self.cname = ""
        self.type = "npc"
        self.amount = 0
        self.title1=""
        self.title2=""
        self.title3=""
        self.status="normal"
    def __str__(self):
        return self.format()
    def format(self,limit=100):
        s1 = "" if self.amount <= 1 else str(self.amount) + " "        
        s2 = "" if self.title1 == "" else self.title1 + " "
        s3 = "" if self.title2 == "" else self.title2 + " "
        s4 = "" if self.title3 == "" else self.title3 + " "
        st = "" if self.status == "normal" else "<" + self.status + ">"
        ret = s1+s2+s3+s4+self.cname + "(" + self.ename + ")" + st
        
        return ret[:min(limit,len(ret))]

class Room(object):
    def __init__(self,env):
        self.env = env
        self.cname = ""
        self.minMap = ""
        self.desc = ""
        self.weather_desc = ""
        self.direction_desc = ""
        self.directions=[]
        self.items = []
        self.npcs = []
        self.isUpdating = True
        self.area = ""
        self.rid = ""
        self.bakid = ""
        self.isct = False
        self.xofct = 0
        self.yofct = 0
        self.zofct = 0
        self.pos_x = 0
        self.pos_y = 0
    def gen_rid(self):
        s = self.area + self.cname + self.desc + str(self.xofct) + str(self.yofct) + str(self.zofct)
        self.rid = md5digest(s)
        s1 = self.area + self.cname + self.desc 
        self.bakid = md5digest(s1)
    def update_xyz(self,preRoom,move):
        self.xofct = preRoom.xofct+self.env.d2x[move]
        self.yofct = preRoom.yofct+self.env.d2y[move]
        self.zofct = preRoom.zofct+self.env.d2z[move]
        
    def adjustPos(self,nodes_pos_dict):      
        print "init pos: " + str(self.pos_x) + "," + str(self.pos_y)
        flag = False
        delta = 0.1
        for i in range(10):
            for j in [i,-1*i]:
                for k in range(i+1):
                    for l in [k,-1*k]:
                        pos_x = self.pos_x + j*delta
                        pos_y = self.pos_y + l*delta
                        flag = False
                        for (npos_x,npos_y) in nodes_pos_dict.values():
                            if math.sqrt((pos_x-npos_x)*(pos_x-npos_x) + (pos_y-npos_y)*(pos_y-npos_y))<0.4:
                                print str(pos_x),str(pos_y),str(npos_x),str(npos_y)
                                flag = True
                                break
                        if not flag:
                            break
                    if not flag:
                        break
                if not flag:
                    break
            if not flag:
                break
        
        self.pos_x = pos_x
        self.pos_y = pos_y

    def getPos(self):
        return (self.pos_x,self.pos_y)
    def clear(self):
        self.directions = []
        self.items = []
        self.npcs = []

    def __str__(self):
        ret = ""
        ret = ret + "room name: " + self.cname + "\n"
        ret = ret + "room min map: " + self.minMap + "\n"
        ret = ret + "room desc: " + self.desc + "\n"
        ret = ret + "room weather desc: " + self.weather_desc + "\n"
        ret = ret + "room direction_desc: " + self.direction_desc + "\n"
        ret = ret + "room directions: " + "\n"
        for d in self.directions:
            ret = ret + d + ";"
        ret = ret + "\n"
        ret = ret + "room items: " + "\n"
        for d in self.items:
            ret = ret + str(d) + "\n"
        ret = ret + "room npcs: " + "\n"
        for d in self.npcs:
            ret = ret + str(d) + "\n"
        return ret
class MudEdge(object):
    def __init__(self,room1,room2,action_from1to2,cost_from1to2):    
        self.room1 = room1
        self.room2 = room2
        self.action_from1to2 = action_from1to2
        self.cost_from1to2 = cost_from1to2

class MudEnviroment(object):
    def __init__(self):
        self.food_dict = {}
        self.drink_dict = {}
        self.wearing_dict = {}
        self.weapon_dict = {}
        self.map_move = {}
        self.d2x = {}
        self.d2y = {}
        self.d2z = {}
        
    def is_food(self,item):
        if item.lower() in self.food_dict.keys():
            return True
        else:
            return False
    def is_drink(self,item):
        if item.lower() in self.drink_dict.keys():
            return True
        else:
            return False
         

class RoleStatus(object):
    def __init__(self):
        self._count_hpbrief = 1
        self.jy = 0 
        self.qn = 0 
        self.max_nl = 0
        self.nl = 0
        self.max_jl = 0
        self.jl = 0
        self.max_qx = 0
        self.e_qx = 0
        self.qx = 0
        self.max_js = 0
        self.e_js = 0
        self.js = 0
        self.zq = 0
        self.zy = 0
        self.sw = 0
        self.ys = 0
        #######score info#############
        self.title1 = ""
        self.title2 = ""
        self.title3 = ""
        self.remark = ""
        self.cname = ""
        self.ename = ""
        self.name_desc = ""
        self.age = ""
        #######items on body###########
        self.items = defaultdict(list)

    #update role status by info of hpbrief
    #经验，潜能，最大内力，当前内力，最大精力，当前精力
    #最大气血，有效气血，当前气血，最大精神，有效精神，当前精神
    #set hpbrief long情况下可另显示一行真气，真元，食物，饮水
    #example:
    #40,309,0,0,100,100
    #100,100,100,125,125,125
    #0,100,139,139,0,0
    def update_hpbrief(self,status):
        #pdb.set_trace()
        if self._count_hpbrief == 1:
            (self.jy,self.qn,self.max_nl,self.nl,self.max_jl,self.jl) = status
        if self._count_hpbrief == 2:
            (self.max_qx,self.e_qx,self.qx,self.max_js,self.e_js,self.js) = status
        if self._count_hpbrief == 3:
            (self.zq,self.zy,self.sw,self.ys,_,_ )= status
        self._count_hpbrief = self._count_hpbrief + 1 if self._count_hpbrief<3 else 1

    def __str__(self):
        
        ret = "jy:" + str(self.jy) + "; " + "qn:" +  str(self.qn) +  "; " + "nl:" +  str(self.nl) +  "; " + "jl:" +  str(self.jl)
        ret = ret + "\n"
        ret = ret + "qx:" + str(self.qx) + "; " + "js:" + str(self.js) + "; " + "sw:" + str(self.sw) + "; " + "ys:" + str(self.ys)
        return ret



#----------------------------------------------------------------------
def getJsonPath(name, moduleFile):
    """
    获取JSON配置文件的路径：
    1. 优先从当前工作目录查找JSON文件
    2. 若无法找到则前往模块所在目录查找
    """
    currentFolder = os.getcwd()
    currentJsonPath = os.path.join(currentFolder, name)
    if os.path.isfile(currentJsonPath):
        return currentJsonPath
    
    moduleFolder = os.path.abspath(os.path.dirname(moduleFile))
    moduleJsonPath = os.path.join(moduleFolder, '.', name)
    return moduleJsonPath


# 加载配置
#----------------------------------------------------------------------
def loadJsonSetting(settingFileName):
    """加载JSON配置"""
    settingFilePath = getJsonPath(settingFileName, __file__)

    setting = {}

    try:
        with open(settingFilePath, 'rb') as f:
            setting = f.read()
            if type(setting) is not str:
                setting = str(setting, encoding='utf8')
            setting = json.loads(setting)
    except:
        traceback.print_exc()
    
    return setting

def timer_check_config_change(settingFileName="setting_files.json",interval=1):
    global file_mtime_dict
    
    settingFilePath = getJsonPath(settingFileName, __file__)
    p = Path(settingFilePath).parent
    files = loadJsonSetting(settingFileName)
    for f in files:
        sfile = p/f["filename"]
        if sfile.exists():
            mtime = sfile.stat().st_mtime
            if file_mtime_dict[f["filename"]] < mtime - 0.1:
                globals()[f["func"]](settingFileName=f["filename"])
                file_mtime_dict[f["filename"]] = mtime        
        
    Timer(interval,timer_check_config_change,kwargs={'settingFileName':settingFileName,'interval':interval}).start()

def loadConfig(settingFileName="config.json"):
    global myConfig
    setting = loadJsonSetting(settingFileName)
    class_config = setting["class"]
    triggers_config = setting["trigger"]
    trigger_dict = {}
    for t in triggers_config:
        trigger_dict[t['name']] = t
    tickers_config = setting["ticker"]
    ticker_dict = {}
    for t in tickers_config:
        ticker_dict[t['name']] = t
    enabled_triggers_set = set()
    enabled_tickers_set = set()
    for c in class_config:
        if c["enabled"]:
            enabled_triggers_set.update(c["trigger"])
            enabled_tickers_set.update(c["ticker"])
    config = defaultdict(list)
    for trigger_name in enabled_triggers_set:
        config["trigger"].append(trigger_dict[trigger_name])
    for ticker_name in enabled_tickers_set:
        config["ticker"].append(ticker_dict[ticker_name])

    myConfig['old_tickers'] = []
    myConfig['current_tickers'] = []
    for t in myConfig["ticker"]:
        myConfig['old_tickers'].append(t["name"])
    myConfig['trigger'] = config["trigger"]
    myConfig['ticker'] = config["ticker"]
    for t in config["ticker"]:
        myConfig['current_tickers'].append(t["name"])   
    start_new_ticker()
    
def loadItems(settingFileName="env.json"):
    setting = loadJsonSetting(settingFileName)
    env.food_dict = setting["food"]
    env.drink_dict = setting["drink"]
    env.map_move = setting["map_move"]
    env.d2x = setting["d2x"]
    env.d2y = setting["d2y"]
    env.d2z = setting["d2z"]

    
    
def clear_cmdfiles():
    p = Path.cwd()    
    f = p/"cmd_files"
    if f.exists():
        for file in f.glob('*'):
            file.unlink()
        #generate a cmd88888888 file to inform tt 
        f = f/"cmd88888888"  
        cmd = "hi"
        with f.open('w',encoding = 'utf8') as file_handle:   # .txt可以不自己新建,代码会自动新建
            file_handle.write(cmd.decode("utf8"))     # 写入



#handle triggers
def trigger_handler(event):
    line = event.dict_['data']
    for t in myConfig["trigger"]:
        globals()[t["func"]](line)

def start_new_ticker():
    for t in myConfig["ticker"]:
        if t["name"] not in myConfig["old_tickers"]:
            ticker_timer(t)

def ticker_timer(t):
    globals()[t["func"]]()
    if t["name"] in myConfig["current_tickers"]:
        for tt in myConfig["ticker"]:
            if tt["name"] == t["name"]:
                t = tt
                break
        Timer(t["interval"], ticker_timer,args=[t]).start()


def sendCmd(cmd):
    global global_cmdIndex
    myevent = Event("line_event")    
    myevent.dict_['data'] = "##cmd:::" + cmd
    rmq.put(myevent)
    #write to cmd files
    p = Path.cwd()    
    f = p/"cmd_files"
    if not f.exists():
        f.mkdir() 

    lock.acquire()
    file_num = len(list(f.glob('*')))
    if file_num>=10:        
        cmdIndex = 99999999
        for file in f.glob('*'):
            if int(file.name[3:])<cmdIndex:
                cmdIndex = int(file.name[3:])                
                oldfilename = file.name        
        ofile = f/oldfilename
        ofile.unlink()    
    filename = "cmd" + str(global_cmdIndex)
    global_cmdIndex = global_cmdIndex + 1  
    
    lock.release()
    f = f/filename  
    with f.open('w',encoding = 'utf8') as file_handle:   # .txt可以不自己新建,代码会自动新建
        file_handle.write(cmd.decode("utf8"))     # 写入
        
###################################################################
#trigger functions###########

def func_hpbrief_update(line):    
    p = re.compile(r'^#(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
    m = p.match(line)
    if m is not None:
        status = (int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))
        mystatus.update_hpbrief(status)

    p = re.compile(r'^>'.decode("utf8"))
    m = p.match(line)
    if m is not None:
        mystatus._count_hpbrief=1


def func_trigger_fillhulu(line):
    p = re.compile(r"^葫芦已经被喝得一滴也不剩了。".decode("utf8"))
    m = p.match(line)
    if m is not None:
        sendCmd("fill hu lu")

def func_trigger_score(line):
    global trigger_flags
    global record_lines
    if len(line)>8 and line[:8] == "##cmd:::":
        return
    p = re.compile(r'^≡━━━━◎人物详情◎━━━━━━━━━━━━━━━━━━━━━━━━━━≡'.decode("utf8"))
    m = p.match(line)
    if m is not None:  
        record_lines["score"] = []
        trigger_flags["score"] = 1
        return
    if trigger_flags["score"] == 1:
        p = re.compile(r'^>'.decode("utf8"))
        m = p.match(line)
        if m is None:
            record_lines["score"].append(line)
            return
        else:
            trigger_flags["score"] = 2
            p = re.compile(r'^ 【(.+?)】(.*?)\((.*?)\)'.decode("utf8"))
            s = p.match(record_lines["score"][0])
            if s is not None:
                mystatus.name_desc = s.group(0)
                ps = re.compile(r" |「|」".decode("utf8"))
                mylist = ps.split(s.group(2).strip(" "))                
                title1=""
                title2=""
                title3=""
                cname=""
                ts = []
                for t in mylist:
                    if t=="":
                        continue
                    ts.append(t)
                if len(ts) == 4:
                    title1 = ts[0]
                    title2 = ts[1]
                    title3 = ts[2]
                    cname = ts[3]
                if len(ts) == 3:
                    title1 = ts[0]
                    title2 = ts[1]                
                    cname = ts[2]
                if len(ts) == 2:
                    title1 = ts[0]                             
                    cname = ts[1]
                if len(ts) == 1:                           
                    cname = ts[0]

                remark = s.group(1)
                ename = s.group(3)
                (mystatus.title1,mystatus.title2,mystatus.title3,mystatus.remark,mystatus.cname,mystatus.ename) = \
                    (title1,title2,title3,remark,cname,ename)                
                for myline in record_lines["score"]:
                    p = re.compile(r'^\s*你是一位(.+?岁)的.*'.decode("utf8"))
                    s = p.match(myline)
                    if s is not None:
                        mystatus.age = s.group(1)                        
                        break
recent_move = None    
def func_trigger_update_roomInfo(line):
    global trigger_flags
    global record_lines
    global current_room
    global pre_room
    global recent_move
    global env
    global G
    global rid_room_dict
    global rid_cname_dict
    global nodes_init_pos
    global min_map

    if len(line)>8 and line[:8] == "##cmd:::":
        if line[8:] in env.map_move.keys():
            recent_move = line[8:]
        if line[8:] in ['l','look']:
            recent_move = "look"
        return
    p = re.compile(r'^(\S+) -\s+$')
    m = p.match(line)
    if m is not None:
        if pre_room is None or recent_move<>"look":
            pre_room = copy.deepcopy(current_room)    
            current_room = Room(env)     
        else:
            current_room.clear()   
        record_lines["look_roomInfo"] = []
        current_room.cname = m.group(1)
        trigger_flags["look_roomInfo"] = 1
        #send hpbrief to accelerate the confirmation of room info
        sendCmd("hpbrief")
        return
    if trigger_flags["look_roomInfo"] == 1:
        p = re.compile(r'^(\s+\S+.*)')
        m = p.match(line)
        if m is not None:
            record_lines["look_roomInfo"].append(line)         
            return
        
        p = re.compile(r'^>'.decode("utf8"))
        m = p.match(line)
        if m is None:
            p = re.compile(r'^(\S+.*)')
            m = p.match(line)
            if m is not None:    
                if len(record_lines["look_roomInfo"]) == 0:
                    return        
                record_lines["look_roomInfo"][-1] = record_lines["look_roomInfo"][-1] + line
                return
        else:
            trigger_flags["look_roomInfo"] = 2     
            #analyse record_lines   

            lines = record_lines["look_roomInfo"]
            desc_start_index = -1
            weather_start_index = -1
            direct_start_index = -1
            items_start_index = -1
            for i,myline in enumerate(lines):
                if items_start_index == -1 and direct_start_index == -1 and weather_start_index == -1 and desc_start_index == -1:
                    p = re.compile(r'^(    \S+.*)')
                    m = p.match(myline)
                    if m is not None:
                        desc_start_index = i
                        continue                    
                    
                if items_start_index == -1 and direct_start_index == -1 and weather_start_index == -1:
                    p = re.compile(r'^\s+(「.*?」:.*)'.decode("utf8"))
                    m = p.match(myline)
                    if m is not None:
                        weather_start_index = i
                        continue

                if items_start_index == -1 and direct_start_index == -1:
                    p = re.compile(r'^\s+这里.*?的.*?有 (.*?)。'.decode("utf8"))
                    m = p.match(myline)
                    if m is not None:
                        direct_start_index = i
                        continue

                if items_start_index == -1:
                    p = re.compile(r'^\s+((一|二|三|四|五|六|七|八|九|十)(块|个|枚|位|只))?(.*?)\((.*?)\)( <(.*?)>)?$'.decode("utf8"))
                    s = p.match(myline)
                    if m is not None:
                        items_start_index = i
                        continue
                    else:
                        continue
                else:
                    break   
            if desc_start_index*weather_start_index*direct_start_index*items_start_index != 0:
                if desc_start_index>0:
                    current_room.minMap = "\n".join(lines[:desc_start_index])                     
                elif weather_start_index>0:
                    current_room.minMap = "\n".join(lines[:weather_start_index])
                elif direct_start_index>0:
                    current_room.minMap = "\n".join(lines[:direct_start_index])
                elif items_start_index>0:
                    current_room.minMap = "\n".join(lines[:items_start_index])
                else:
                    current_room.minMap = "\n".join(lines)
            if desc_start_index>=0:
                if weather_start_index>0:
                    current_room.desc = "\n".join(lines[desc_start_index:weather_start_index])
                elif direct_start_index>0:
                    current_room.desc = "\n".join(lines[desc_start_index:direct_start_index])
                elif items_start_index>0:
                    current_room.desc = "\n".join(lines[desc_start_index:items_start_index])
                else:
                    current_room.desc = "\n".join(lines[desc_start_index:])
            if weather_start_index>=0:
                if direct_start_index>0:
                    current_room.weather_desc = "\n".join(lines[weather_start_index:direct_start_index])
                elif items_start_index>0:
                    current_room.weather_desc = "\n".join(lines[weather_start_index:items_start_index])
                else:
                    current_room.weather_desc = "\n".join(lines[weather_start_index:])
            if direct_start_index>=0:                
                p = re.compile(r'^\s+这里.*?的.*?有 (.*?)。'.decode("utf8"))
                m = p.match(lines[direct_start_index])
                if m is not None:                        
                    current_room.direction_desc = m.group(1)
                    p = re.compile(r'、| 和 '.decode("utf8"))
                    current_room.directions = sorted(list(p.split(current_room.direction_desc)))
            if items_start_index>=0:
                for myline in lines[items_start_index:]:
                    p = re.compile(r'^\s*((一|二|三|四|五|六|七|八|九|十)(块|个|枚|位|只))?(.*?)\((.*?)\)( <(.*?)>)?$'.decode("utf8"))
                    s = p.match(myline)
                    if s is not None:                
                        num = 1
                        if s.group(2) is not None:
                            num = to_numbers(s.group(2))
                        ps = re.compile(r" |「|」".decode("utf8"))
                        mylist = ps.split(s.group(4).strip(" "))
                        itype = "npc"
                        title1=""
                        title2=""
                        title3=""
                        cname=""
                        ts = []
                        for t in mylist:
                            if t=="":
                                continue
                            ts.append(t)
                        if len(ts) == 4:
                            title1 = ts[0]
                            title2 = ts[1]
                            title3 = ts[2]
                            cname = ts[3]
                        if len(ts) == 3:
                            title1 = ts[0]
                            title2 = ts[1]                
                            cname = ts[2]
                        if len(ts) == 2:
                            title1 = ts[0]                             
                            cname = ts[1]
                        if len(ts) == 1:                           
                            cname = ts[0]
                            itype = "item"
                        
                        ename = s.group(5)
                        status = s.group(7)
                        if status is None:
                            status = "normal"
                        if itype == "item":
                            muditem = MudItem()
                            muditem.ename = ename
                            muditem.cname = cname
                            if env.is_drink(ename):
                                muditem.type = "drink"
                            if env.is_food(ename):
                                muditem.type = "food"
                            muditem.amount = num
                            current_room.items.append(muditem)
                        else:
                            mudnpc = MudNpc()
                            mudnpc.ename = ename
                            mudnpc.cname = cname
                            mudnpc.type = "npc"
                            mudnpc.amount = num
                            mudnpc.title1 = title1
                            mudnpc.title2 = title2
                            mudnpc.title3 = title3
                            mudnpc.status = status
                            current_room.npcs.append(mudnpc)
            current_room.isUpdating = False
            if pre_room is not None and len(pre_room.cname)>0 and recent_move == "look":
                return
            #store room and edge in G:            
            if len(pre_room.cname)>0:
                current_room.update_xyz(pre_room,recent_move)
                current_room.gen_rid()
                G.add_edge(pre_room.rid,current_room.rid,move=recent_move,weight=1)  
                if current_room.rid not in nodes_init_pos.keys():  
                    print "changing room pos: " +    current_room.rid               
                    current_room.pos_x = pre_room.pos_x + current_room.env.d2x[recent_move]
                    current_room.pos_y = pre_room.pos_y - current_room.env.d2y[recent_move]
                    current_room.adjustPos(nodes_init_pos)    
                else:
                    current_room.pos_x = rid_room_dict[current_room.rid].pos_x
                    current_room.pos_y = rid_room_dict[current_room.rid].pos_y
            else:
                current_room.gen_rid()                
                G.add_node(current_room.rid)
            #fixed_nodes = copy.copy(list(nodes_init_pos.keys()))
            if current_room.rid not in nodes_init_pos.keys():           
                nodes_init_pos[current_room.rid] = current_room.getPos()                
                rid_cname_dict[current_room.rid] = current_room.cname
            rid_room_dict[current_room.rid] = copy.deepcopy(current_room)

            if recent_move is not None:
                print "recent_move: " + recent_move
            print "pre room:" + pre_room.rid 
            print "pre room posx: " + str(pre_room.pos_x)
            print "pre room posy: " + str(pre_room.pos_y)
            print "current room:" + current_room.rid
            print nodes_init_pos
            #generate figure of G
            plt.figure(figsize=(cfg_gui.gps_rec[2]/100.0,cfg_gui.gps_rec[3]/100.0))
            plt.rcParams['savefig.dpi'] = 100 #图片像素
            plt.rcParams['figure.dpi'] = 100 #分辨率
            #nodes_init_pos = nx.spring_layout(G,iterations=10,fixed=fixed_nodes,pos=nodes_init_pos)
            colors = []
            for n in list(G.nodes):
                if n==current_room.rid:
                    colors.append("red")
                else:
                    colors.append("grey")
                

            nx.draw(G,pos=nodes_init_pos, node_size=200,  edge_color="blue",node_color=colors, font_size=10, with_labels=True,labels=rid_cname_dict, font_family ='SimHei')
            plt.savefig('min_map.png', dpi=100, transparent=True)
            


            


########################################################################
#ticker functions######################
def func_t_hpbrief():
    cmd = "hpbrief"
    sendCmd(cmd)

def func_t_skills():
    sendCmd("skills")

def func_t_getFoodDrink():
    rmq.register("line_event",look_get_food_handler)
    cmd = "look"
    sendCmd(cmd)
    sleep(5)
    rmq.unregister("line_event",look_get_food_handler)

def func_t_update_roomInfo():    
    cmd = "look"
    sendCmd(cmd)
    
#########################################################################
##other function#################################
def to_numbers(ch):
    n_dict = {"一":1,\
              "二":2,\
              "三":3,\
              "四":4,\
              "五":5,\
              "六":6,\
              "七":7,\
              "八":8,\
              "九":9,\
              "十":10}
    return n_dict[ch.encode("utf8")]

def look_get_food_handler(event):
    line = event.dict_['data']
    p = re.compile(r'^    \S+\((.*?)\)')
    m = p.match(line)
    if m is not None:
        item = m.group(1).lower()
        if env.is_food(item):
            sendCmd("get " + item)
            sendCmd("eat " + item)
        if env.is_drink(item):
            sendCmd("get " + item)
            sendCmd("drink " + item)

def cmd_pack(action,item):
    ret = action + " " + item.ename.lower()
    if action.lower()=="get all":
        ret = action
    return ret
                        

#line print out handler
def simpleoutput_handler(event):
    print(u'处理事件：{}:{}'.format(event.type_,event.dict_['data'] ))        
#classify msg into:cmd response msg(cmd),channel msg(channel)
def msg_classify_handler(event):
    global cmd_queue
    global record_lines
    global cache_resp
    
    line = event.dict_['data']
    if len(line.strip()) == 0: 
        return
    p = re.compile(r'^##cmd:::(.*)'.decode("utf8"))
    m = p.match(line)
    if m is not None:
        cmd_queue.put(m.group(1))        

    p = re.compile(r'^【(.+?)】.*'.decode("utf8"))
    m = p.match(line)
    if m is not None:
        mytype = m.group(1)
        channel_info = {"type":mytype,"resp":line}
        cache_resp["channel"].append(channel_info)
        if len(cache_resp["channel"]) > CACHE_SIZE:
            cache_resp["channel"] = cache_resp["channel"][len(cache_resp["channel"]) - CACHE_SIZE:]
        #debug:
        print(u'{}:{}'.format(channel_info["type"],channel_info["resp"] ))        
        return
    else:
        p = re.compile(r'^>'.decode("utf8"))
        m = p.match(line)
        if m is None:
            if cmd_queue.empty():
                cache_resp["other"].append(line)
                if len(cache_resp["other"]) > CACHE_SIZE:
                    cache_resp["other"] = cache_resp["other"][len(cache_resp["other"]) - CACHE_SIZE:]
                #debug
                print(u'{}:{}'.format("other resp",line))    
            else:           
                record_lines["cmd"].append(line)
            return
        else:
            command_str = ""
            if not cmd_queue.empty():
                command_str=cmd_queue.get()
            mylines = copy.copy(record_lines["cmd"])
            resp = mylines
            other_resp = []            
            for i,l in enumerate(mylines):
                if l.startswith("##cmd:::"):
                    resp = mylines[i+1:]
                    other_resp = mylines[:i]            
            cmd_info = {"command":command_str,"resp":resp}
            record_lines["cmd"] = []
            cache_resp["cmd"].append(cmd_info)
            if len(cache_resp["cmd"]) > CACHE_SIZE:
                cache_resp["cmd"] = cache_resp["cmd"][len(cache_resp["cmd"]) - CACHE_SIZE:]
            #other resp:
            for l in other_resp:
                if l.startswith("##cmd:::"):
                    continue
                cache_resp["other"].append(l)
                if len(cache_resp["other"]) > CACHE_SIZE:
                    cache_resp["other"] = cache_resp["other"][len(cache_resp["other"]) - CACHE_SIZE:]
            #debug:
            print(u'{}:{}'.format(cmd_info["command"],"/n".join(cmd_info["resp"] )))     
            print(u'{}:{}'.format("other resp","/n".join(other_resp) ))       
            return
    
    
###########################################################################

def initGame():
	# 初始化pygame, 设置展示窗口
	pygame.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode(cfg_gui.SCREENSIZE)
	pygame.display.set_caption('pkuxkx')
	# 加载必要的游戏素材
	game_images = {}
	for key, value in cfg_gui.IMAGE_PATHS.items():
		game_images[key] = pygame.image.load(value)
	game_sounds = {}
	for key, value in cfg_gui.SOUNDS_PATHS.items():
		if key != 'moonlight':
			game_sounds[key] = pygame.mixer.Sound(value)
	return screen, game_images, game_sounds

def drawText(content,font,color=(255,255,255)):
    text_sf  =  font.render(content,True,color)
    return  text_sf 

def drawMultilineText(screen,content,fontName,rect,line_space=5,max_font_size=18,color=(255,255,255)):
    (left,top,width,height) = rect
    if content is None or len(content) == 0:
        return 
    content = content.replace("\n","")
    if width<10 or height<10:
        return     
    font_size = int((math.sqrt(line_space*line_space + 4*(width-10)*(height-10)/len(content))-line_space)/2)
    if font_size<1:
        font_size = 1
    font_size = min(font_size,max_font_size)
    pygame.font.init()
    font  =  pygame.font.Font(fontName, font_size)
    row_length = (width-10)//font_size
    row_num = len(content)/row_length
    for i in range(row_num):
        text_sf  =  font.render(content[i*row_length:(i+1)*row_length],True,color)
        screen.blit(text_sf,(left,top+i*(font_size+line_space)))
    if row_num*row_length < len(content):
        text_sf  =  font.render(content[row_num*row_length:],True,color)
        screen.blit(text_sf,(left,top+row_num*(font_size+line_space)))
###########################################################################
class Button():
    def __init__(self,screen,bgimg,icon,msg,font,font_color,rect,clicked=False):
        self.screen = screen
        self.bgimg = bgimg
        self.icon = icon
        self.msg = msg
        self.rect = rect
        self.font = font
        self.font_color = font_color
        self.clicked = clicked

    def draw_button(self):        
        self.screen.blit(self.bgimg,(self.rect.left,self.rect.top))
        #draw icon
        if self.icon is not None:
            self.screen.blit(self.icon,(self.rect.left+2,self.rect.top))
        #draw text
        if self.msg is not None:
            text_sf  =  self.font.render(self.msg,True,self.font_color)
            if self.icon is not None:
                self.screen.blit(text_sf,(self.rect.left+self.icon.get_rect().width+2,self.rect.top+1))
            else:
                self.screen.blit(text_sf,(self.rect.left+2,self.rect.top+2))
        #draw a opatical surface on it if not selected:
        if not self.clicked:
            s = pygame.Surface((self.rect.width, self.rect.height))
            s = s.convert_alpha()
            s.fill((255,255,255,0))
            pygame.draw.rect(s, (30, 41, 61, 60),pygame.Rect(0,0,self.rect.width, self.rect.height))
            self.screen.blit(s, (self.rect.left, self.rect.top))

class CheckButton():
    def __init__(self,screen,bgimg,msg,font,font_color,rect,checked=False):
        self.screen = screen
        self.bgimg = bgimg        
        self.msg = msg
        self.rect = rect
        self.font = font
        self.font_color = font_color
        self.checked = checked
    def draw_button(self):        
        self.screen.blit(self.bgimg,(self.rect.left,self.rect.top))
        #draw icon        
        icon = pygame.image.load(cfg_gui.IMAGE_PATHS['checked'])            
        if not self.checked:
            icon = pygame.image.load(cfg_gui.IMAGE_PATHS['unchecked'])
        self.screen.blit(icon,(self.rect.left+2,self.rect.top))
        #draw text
        if self.msg is not None:
            text_sf  =  self.font.render(self.msg,True,self.font_color)
            self.screen.blit(text_sf,(self.rect.left+icon.get_rect().width+4,self.rect.top+1))
            
def check_button(button_list, mouse_x , mouse_y):
    for i,bt in enumerate(button_list):
        if bt.rect.collidepoint(mouse_x , mouse_y):
            return i
    return -1
def drawTwindow(screen,filter_checked_dict,content_top,content_bottom):
    s_terminal = pygame.Surface((cfg_gui.twindows_rec[2],cfg_gui.twindows_rec[3]))
    s_terminal = s_terminal.convert_alpha()
    s_terminal.fill((255,255,255,0))
    pygame.draw.rect(s_terminal, (0,0,0,200), pygame.Rect(0,0,cfg_gui.twindows_rec[2],cfg_gui.twindows_rec[3]))

    #draw content_top,content_top is a line list:
    font_size = 16
    color=(255,255,255,200)
    font  =  pygame.font.Font('wqy-zenhei.ttc', font_size)
    row_length = (cfg_gui.twindows_rec1[2])//font_size
    max_row_num = (cfg_gui.twindows_rec1[3])//(font_size+1)
    counter_row = 0
    text_sf_list = []
    for line in content_top[::-1]:        
        row_num = len(line)/row_length
        counter_row = counter_row + row_num
        if counter_row+1>max_row_num:
            break
        line_row_list = []
        for i in range(row_num):
            text_sf  =  font.render(line[i*row_length:(i+1)*row_length],True,color)
            line_row_list.append(text_sf)
        if row_num*row_length < len(line):            
            text_sf  =  font.render(line[row_num*row_length:],True,color) 
            line_row_list.append(text_sf)
            counter_row = counter_row + 1
        text_sf_list.extend(line_row_list[::-1])
    text_sf_list.reverse()
   
    for i,t in enumerate(text_sf_list):
        s_terminal.blit(t,(0,i*(font_size+1)))
    #draw content_bottom,content_bottom is a line list:
    
    max_row_num = (cfg_gui.twindows_rec2[3])//(font_size+1)
    counter_row = 0
    text_sf_list = []
    for line in content_bottom[::-1]:        
        row_num = len(line)/row_length
        counter_row = counter_row + row_num
        if counter_row+1>max_row_num:
            break
        line_row_list = []
        for i in range(row_num):
            text_sf  =  font.render(line[i*row_length:(i+1)*row_length],True,color)
            line_row_list.append(text_sf)
        if row_num*row_length < len(line):            
            text_sf  =  font.render(line[row_num*row_length:],True,color) 
            line_row_list.append(text_sf)
            counter_row = counter_row + 1
        text_sf_list.extend(line_row_list[::-1])
    text_sf_list.reverse()
   
    for i,t in enumerate(text_sf_list):
        s_terminal.blit(t,(0,cfg_gui.twindows_rec1[3]+30+i*(font_size+1)))


    #draw split 
    pygame.draw.line(s_terminal,(255,255,255,200),(0,cfg_gui.twindows_rec1[3]),\
        (cfg_gui.twindows_rec1[2],cfg_gui.twindows_rec1[3]))
    pygame.draw.line(s_terminal,(255,255,255,200),(0,cfg_gui.twindows_rec1[3]+30),\
        (cfg_gui.twindows_rec2[2],cfg_gui.twindows_rec1[3]+30))
    #draw filter text:
    filter_font = pygame.font.Font('wqy-zenhei.ttc', 15)
    filter_words = u"不显示这些："
    s_terminal.blit(drawText(filter_words,filter_font,color=(255,255,255,255)),(2,cfg_gui.twindows_rec1[3]+4))
    check_bt_list = []
    for i,cmd in enumerate(["hpbrief","score","skills","look"]):
        bgimg = pygame.Surface((80,20))
        pygame.draw.rect(bgimg, (0,0,0,0), pygame.Rect(0,0,80,20))
        msg = cmd
        font_color = (255,255,255)
        rect = pygame.Rect(80+i*100,cfg_gui.twindows_rec1[3]+4,80,20)
        check_bt = CheckButton(s_terminal,bgimg,msg,filter_font,font_color,rect,filter_checked_dict[cmd])
        check_bt.draw_button()
        check_bt_list.append(check_bt)
    screen.blit(s_terminal,(cfg_gui.twindows_rec[0],cfg_gui.twindows_rec[1]))
    return check_bt_list

    
def sendCmdCallback(textbox):   
    cmd = textbox.text 
    if len(cmd.strip())>0:
        sendCmd(cmd.strip())
    
#############################################################################
env = MudEnviroment()
mystatus =  RoleStatus()
current_room = Room(env)
pre_room = None
rmq= RedisMQ()
  
def main(args):    
    clear_cmdfiles()
    #rmq.register("line_event",simpleoutput_handler)
    rmq.register("line_event",msg_classify_handler)
    rmq.start() 
    print("redis message queue has started.")   
    rmq.register("line_event",trigger_handler)
    timer_check_config_change(settingFileName="setting_files.json",interval=1)
    

    ####pygame code here######################

    # 初始化
    screen, game_images, game_sounds = initGame()
    min_map = pygame.image.load('min_map.png')
    # 播放背景音乐
    pygame.mixer.music.load(cfg_gui.SOUNDS_PATHS['moonlight'])
    pygame.mixer.music.play(-1, 0.0)
    pygame.font.init()
    simhei_font  =  pygame.font.Font('simhei.ttf', 12)
    #use for qx/js bar
    qx_value = 100
    js_value = 100

    clock = pygame.time.Clock()
    
    selected_item = None
    selected_npc = None
    selected_action = None

    filter_checked_dict = defaultdict(bool)
    cmd_window_showed = False
    filter_checked_dict={
        'hpbrief':True,
        "look":True,
        "score":True,
        "skills":True
    }
    check_bt_list = []

    drawing_room = copy.deepcopy(current_room)
    cmdline_input_rect = pygame.Rect(cfg_gui.command_line_rec[0]+25,cfg_gui.command_line_rec[1]+1,cfg_gui.command_line_rec[2]-40,cfg_gui.command_line_rec[3])
    cmd_font = pygame.font.Font('simhei.ttf', 16)
    cmdline_box = TextBox(screen,cmdline_input_rect,font=cmd_font, callback=sendCmdCallback)


    keep=True    
    while keep:
        sleep(0.1)
        screen.fill(0)
        #draw background
        for x in range(cfg_gui.SCREENSIZE[0]//game_images['grass'].get_width()+1):
			for y in range(cfg_gui.SCREENSIZE[1]//game_images['grass'].get_height()+1):
				screen.blit(game_images['grass'], (x*100, y*100))
        #draw qx and js status bar
        screen.blit(drawText(u'气血:',simhei_font),(5,5))
        screen.blit(game_images.get('healthbar'), (40, 5))
        screen.blit(drawText(str(mystatus.qx) + "/" + str(mystatus.max_qx),simhei_font),(145,5))
        if mystatus.max_qx>0:
            for i in range(int(qx_value*mystatus.qx/mystatus.max_qx)):
                screen.blit(game_images.get('health'), (i+43, 8))
        screen.blit(drawText(u'精神:',simhei_font),(5,20))
        screen.blit(game_images.get('healthbar'), (40, 20))
        screen.blit(drawText(str(mystatus.js) + "/" + str(mystatus.max_js),simhei_font),(145,20))
        if mystatus.max_js>0:
            for i in range(int(js_value*mystatus.js/mystatus.max_js)):
                screen.blit(game_images.get('health'), (i+43, 23))
        # draw role name
        screen.blit(drawText(mystatus.age + " " + mystatus.name_desc,pygame.font.Font('simhei.ttf', 16),color=(64,64,64)),(200,10))
        #draw horizotal split 
        for x in range(cfg_gui.SCREENSIZE[0]//game_images['split1'].get_width()+1):
			screen.blit(game_images['split1'], (x*27, 40))
        #draw vertical split 
        #for x in range((cfg_gui.SCREENSIZE[1]-cfg_gui.gps_rec[1])//game_images['split2'].get_height()+1):
		#	screen.blit(game_images['split2'], (cfg_gui.gps_rec[0], cfg_gui.gps_rec[1]+x*27))

        #deep copy current_room into drawing_room avoiding reading inconsistance
        if not current_room.isUpdating:
            drawing_room = copy.deepcopy(current_room)
        # draw room name
        room_name_font = pygame.font.Font('simhei.ttf', 20)
        screen.blit(drawText(drawing_room.cname,room_name_font),(cfg_gui.room_desc_rec[0] + cfg_gui.room_desc_rec[2]/2 - 50 ,cfg_gui.room_desc_rec[1] - 30))
        # draw room desc
        fontName = 'simhei.ttf'
        content = drawing_room.desc        
        drawMultilineText(screen,content,fontName,cfg_gui.room_desc_rec,line_space=5)
        # draw room items and npcs
        item_button_list = []
        item_list = []
        item_rows = int(math.ceil(len(drawing_room.items)/3.0))
        for i in range(item_rows):
            for j in range(3):                
                if 3*i + j < len(drawing_room.items):
                    icon = game_images['unknown']
                    if drawing_room.items[3*i + j].type=="food":
                        icon = game_images['food']
                    if drawing_room.items[3*i + j].type=="drink":
                        icon = game_images['drink'] 
                    bgimg = game_images['itembg']
                    item_font = pygame.font.Font('simhei.ttf', 14)
                    font_color = (64,64,64)
                    content = str(drawing_room.items[3*i + j].amount) + " " + drawing_room.items[3*i + j].cname + "(" + drawing_room.items[3*i + j].ename + ")"
                    rect = pygame.Rect(cfg_gui.room_items_rec[0]+j*170,cfg_gui.room_items_rec[1]+i*25,bgimg.get_rect().width,bgimg.get_rect().height)
                    clicked = True if selected_item is not None and drawing_room.items[3*i + j].ename == selected_item.ename else False
                    item_button = Button(screen,bgimg,icon,content,item_font,font_color,rect,clicked)
                    item_button.draw_button()

                    item_list.append(drawing_room.items[3*i + j])
                    item_button_list.append(item_button)

        npc_button_list = []
        npc_list = []            
        npcs_per_row = 2
        npc_rows = int(math.ceil(len(drawing_room.npcs)/(npcs_per_row+0.0)))
        room_npcs_rec = (cfg_gui.room_items_rec[0],cfg_gui.room_items_rec[1] + item_rows*25,cfg_gui.room_items_rec[2],cfg_gui.room_items_rec[3])
        for i in range(npc_rows):
            for j in range(npcs_per_row):                
                if npcs_per_row*i + j < len(drawing_room.npcs):
                    bgimg = game_images['npcbg']
                    icon = game_images['npc']   
                    npc_font = pygame.font.Font('simhei.ttf', 14)
                    font_color = (64,64,64) 
                    content = drawing_room.npcs[npcs_per_row*i + j].format(19)
                    rect = pygame.Rect(room_npcs_rec[0]+j*260,room_npcs_rec[1]+i*25,bgimg.get_rect().width,bgimg.get_rect().height)
                    clicked = True if selected_npc is not None and drawing_room.npcs[npcs_per_row*i + j].ename == selected_npc.ename else False
                    npc_button = Button(screen,bgimg,icon,content,npc_font,font_color,rect,clicked)
                    npc_button.draw_button()                
                   
                    npc_list.append(drawing_room.npcs[npcs_per_row*i + j])
                    npc_button_list.append(npc_button)

        #draw action buttons
        action_button_list = []
        action_list = []           
        if selected_item is not None or selected_npc is not None:            
            item = selected_item if selected_item is not None else selected_npc
            #check if selected item or npc is still in room:
            flag = False
            for i in item_list:
                if i.ename == item.ename:
                    flag = True
                    break
            for i in npc_list:
                if i.ename == item.ename:
                    flag = True
                    break
            if flag:#still in room
                content = u"对 "+item.cname + "(" + item.ename+ ")" + u" 做什么？"
                font = pygame.font.Font('simhei.ttf', 16)    
                screen.blit(drawText(content,font,color=(255,255,255)),(cfg_gui.action_area_rec[0],cfg_gui.action_area_rec[1]))
                msgs = cfg_gui.itemInRoom_buttonMsg_dict[item.type]
                mylength = len(msgs)   
                per_row = 5
                rows = int(math.ceil(mylength/(per_row+0.0)))
                for i in range(rows):
                    for j in range(per_row):  
                        index = per_row*i + j              
                        if index < mylength:
                            msg = msgs[index]
                            bgimg = game_images['action_button_bg1'] 
                            if msg in ['kill','hit']:
                                bgimg = game_images['action_button_bg2'] 
                            icon = None   
                            msg_font = pygame.font.Font('simhei.ttf', 16)
                            font_color = (255,255,255)             
                            rect = pygame.Rect(cfg_gui.action_area_rec[0]+j*100,20+cfg_gui.action_area_rec[1]+i*25,bgimg.get_rect().width,bgimg.get_rect().height)
                            clicked = True if selected_action is not None and msg == selected_action else False
                            action_button = Button(screen,bgimg,icon," " + msg,msg_font,font_color,rect,clicked)
                            action_button.draw_button() 

                            action_list.append(msg)
                            action_button_list.append(action_button)
            else:#not in room,maybe left or room changed
                selected_item = None 
                selected_npc = None 
                cmdline_box.text = ""

        #draw command line
        cmdline_bgimg = game_images['cmdline']
        icon = game_images['cmdline_icon']   
        font_color = (255,255,255) 
        content = None
        rect = pygame.Rect(cfg_gui.command_line_rec[0],cfg_gui.command_line_rec[1],cmdline_bgimg.get_rect().width,cmdline_bgimg.get_rect().height)
        clicked = True 
        cmdline_bg = Button(screen,cmdline_bgimg,icon,content,pygame.font.Font('simhei.ttf', 16),font_color,rect,clicked)
        cmdline_bg.draw_button()                

        #draw cmdline text box
        cmdline_box.draw()

        #draw cmdline send button
        sendimg = game_images['cmdline_bt']
        rect = pygame.Rect(cfg_gui.command_line_rec[0]+cmdline_bgimg.get_rect().width+10,cfg_gui.command_line_rec[1],sendimg.get_rect().width,sendimg.get_rect().height)        
        cmdline_bt = Button(screen,sendimg,None,None,pygame.font.Font('simhei.ttf', 16),font_color,rect,True)
        cmdline_bt.draw_button() 

        #draw button to pop out terminal-like window
        cmd_window_img = game_images['cmd_window']
        rect = pygame.Rect(cfg_gui.command_line_rec[0]+cmdline_bgimg.get_rect().width+sendimg.get_rect().width+20,cfg_gui.command_line_rec[1],cmd_window_img.get_rect().width,cmd_window_img.get_rect().height)        
        cmd_window_bt = Button(screen,cmd_window_img,None,None,pygame.font.Font('simhei.ttf', 16),font_color,rect,True)
        cmd_window_bt.draw_button() 
        #draw terminal-like windown
        if cmd_window_showed: 
            content_top = []
            content_bottom = []        
            for resp in cache_resp['cmd']:
                if filter_checked_dict.has_key(resp["command"]) and filter_checked_dict[resp["command"]]:
                    continue
                if len(resp["command"])>0:
                    content_top.append(resp["command"])
                content_top.extend(resp["resp"])
            for resp in cache_resp['other']:
                content_bottom.append(resp)
            check_bt_list = drawTwindow(screen,filter_checked_dict,content_top,content_bottom)
        #draw direction rec surface
        direction_surface = pygame.Surface((cfg_gui.direction_rec[2], cfg_gui.direction_rec[3])).convert_alpha()
        direction_surface.fill((255,255,255,0))
        direction_bg = game_images['direction_bg']
        #direction_surface.blit(direction_bg, (0, 0))
        #draw the direct rec 
        direction_rect_list = []
        for d in current_room.directions:
            try:
                d_rect =cfg_gui.direction_rec_dict[d.lower()]
            except Exception as e:
                continue
            direction_rect_list.append((d,d_rect))
            direction_surface.blit(direction_bg,(d_rect.left,d_rect.top),d_rect)
        screen.blit(direction_surface,(cfg_gui.direction_rec[0], cfg_gui.direction_rec[1]))
        #draw min-map   
        try:
            min_map = pygame.image.load('min_map.png')     
            screen.blit(min_map,(cfg_gui.gps_rec[0],cfg_gui.gps_rec[1]))
        except Exception as e:
            print e

        #event handle:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                keep=False
            elif event.type == pygame.KEYDOWN:
                cmdline_box.key_down(event)
                if cmdline_box.focused and event.key==301:
                    cmdline_box.text = ""
            elif event.type == pygame.MOUSEBUTTONDOWN:                
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if not cmd_window_showed:
                    item_index = check_button(item_button_list, mouse_x , mouse_y)
                    npc_index = check_button(npc_button_list, mouse_x , mouse_y)
                    if item_index>-1 or npc_index>-1:
                        if item_index>-1:
                            selected_item = item_list[item_index]             
                        else:
                            selected_item = None                    
                        if npc_index>-1:
                            selected_npc = npc_list[npc_index]
                        else:
                            selected_npc = None
                    action_button_index = check_button(action_button_list,mouse_x , mouse_y)
                    if action_button_index>-1:
                        selected_action = action_list[action_button_index]  
                        if selected_item is not None or selected_npc is not None: 
                            item = selected_item if selected_item is not None else selected_npc
                            cmd = cmd_pack(selected_action,item)
                            cmdline_box.text = cmd            
                    else:
                        selected_action = None

                if cmdline_bg.rect.collidepoint(mouse_x , mouse_y):
                    cmdline_box.focused = True
                else:
                    cmdline_box.focused = False

                #cmd line bt clicked:send command
                if cmdline_bt.rect.collidepoint(mouse_x , mouse_y) and len(cmdline_box.text)>0:
                    sendCmd(cmdline_box.text.strip())
                    cmd_window_showed = True
                    cmdline_box.text = ""

                #cmd_window bt clicked:pop out terminal-like window
                if cmd_window_bt.rect.collidepoint(mouse_x , mouse_y):
                    cmd_window_showed = not cmd_window_showed    

                #check filter button 
                for bt in check_bt_list:
                    rect = pygame.Rect(bt.rect.left+cfg_gui.twindows_rec[0],bt.rect.top+cfg_gui.twindows_rec[1],bt.rect.width,bt.rect.height)
                    if rect.collidepoint(mouse_x , mouse_y):
                        filter_checked_dict[bt.msg] = not filter_checked_dict[bt.msg]

                #check if direction rec is clicked:
                for (d,d_rect) in direction_rect_list:                          
                    if d_rect.collidepoint(mouse_x-cfg_gui.direction_rec[0], mouse_y-cfg_gui.direction_rec[1]):
                        sendCmd(d)
                        


        clock.tick(10)
        pygame.display.flip()
        #pygame.display.update()
    pygame.quit()

    """ while True:
        sleep(30)        
        #repeatly print some info 
        print mystatus
        print myConfig
        print current_room """
        
    #rmq.stop()


if __name__=="__main__":
    main(sys.argv)