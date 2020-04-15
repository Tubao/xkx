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
from gui_tools import TextBox

reload(sys)
sys.setdefaultencoding('utf8')

myConfig = {"ticker":[],"current_tickers":[]}
lock = Lock()
global_cmdIndex = 0
file_mtime_dict = defaultdict(float)
trigger_flags = defaultdict(int)
record_lines = defaultdict(list)

############################################################################
#########             major classes           ################
#############################################################################
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
    


class MudEnviroment(object):
    def __init__(self):
        self.food_dict = {}
        self.drink_dict = {}
        self.wearing_dict = {}
        self.weapon_dict = {}
        
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
    
def loadItems(settingFileName="items.json"):
    setting = loadJsonSetting(settingFileName)
    env.food_dict = setting["food"]
    env.drink_dict = setting["drink"]
    
def clear_cmdfiles():
    p = Path.cwd()    
    f = p/"cmd_files"
    if f.exists():
        for file in f.glob('*'):
            file.unlink()


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
#record cmd response put it into cmd channel
def func_trigger_cmd_response_record(line):
    pass

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
    
def func_trigger_update_roomInfo(line):
    global trigger_flags
    global record_lines
    global current_room
    if len(line)>8 and line[:8] == "##cmd:::":
        return
    p = re.compile(r'^(\S+) -\s+$')
    m = p.match(line)
    if m is not None:        
        current_room = Room(env)        
        record_lines["look_roomInfo"] = []
        current_room.cname = m.group(1)
        trigger_flags["look_roomInfo"] = 1
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
                current_room.direction_desc = lines[direct_start_index]
                p = re.compile(r'^\s+这里.*?的.*?有 (.*?)。'.decode("utf8"))
                m = p.match(current_room.direction_desc)
                if m is not None:                        
                    dstr = m.group(1)
                    p = re.compile(r'、| 和 '.decode("utf8"))
                    current_room.directions = list(p.split(dstr))
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
        #draw a tick on icon if selected:
        if not self.clicked:
            #self.screen.blit(self.icon,(self.rect.left+50,self.rect.top))
            s = pygame.Surface((self.rect.width, self.rect.height))
            s = s.convert_alpha()
            s.fill((255,255,255,0))
            pygame.draw.rect(s, (30, 41, 61, 60),pygame.Rect(0,0,self.rect.width, self.rect.height))
            self.screen.blit(s, (self.rect.left, self.rect.top))


def check_button(button_list, mouse_x , mouse_y):
    for i,bt in enumerate(button_list):
        if bt.rect.collidepoint(mouse_x , mouse_y):
            return i
    return -1

def sendCmdCallback(cmd):    
    if len(cmd.strip())>0:
        sendCmd(cmd.strip())
#############################################################################
env = MudEnviroment()
mystatus =  RoleStatus()
current_room = Room(env)
rmq= RedisMQ()
  
def main(args):    
    clear_cmdfiles()
    rmq.register("line_event",simpleoutput_handler)
    rmq.start()
    timer_check_config_change(settingFileName="setting_files.json",interval=1)
    rmq.register("line_event",trigger_handler)
    print("redis message queue has started.")    

    ####pygame code here######################

    # 初始化
    screen, game_images, game_sounds = initGame()
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
    drawing_room = copy.deepcopy(current_room)
    cmdline_input_rect = pygame.Rect(cfg_gui.command_line_rec[0]+25,cfg_gui.command_line_rec[1]+1,cfg_gui.command_line_rec[2]-40,cfg_gui.command_line_rec[3])
    cmd_font = pygame.font.Font('simhei.ttf', 16)
    cmdline_box = TextBox(cmdline_input_rect,font=cmd_font, callback=sendCmdCallback)


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
        for x in range((cfg_gui.SCREENSIZE[1]-cfg_gui.gps_rec[1])//game_images['split2'].get_height()+1):
			screen.blit(game_images['split2'], (cfg_gui.gps_rec[0], cfg_gui.gps_rec[1]+x*27))

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
        cmdline_box.draw(screen)

        #draw cmdline send button
        bgimg = game_images['cmdline_bt']
        rect = pygame.Rect(cfg_gui.command_line_rec[0]+cmdline_bgimg.get_rect().width+10,cfg_gui.command_line_rec[1],bgimg.get_rect().width,bgimg.get_rect().height)        
        cmdline_bt = Button(screen,bgimg,None,None,pygame.font.Font('simhei.ttf', 16),font_color,rect,True)
        cmdline_bt.draw_button() 


        #event handle:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                keep=False
            elif event.type == pygame.KEYDOWN:
                cmdline_box.key_down(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:                
                mouse_x,mouse_y = pygame.mouse.get_pos()
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