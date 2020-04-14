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
        self.type = ""
        self.amount = 0
    def __str__(self):
        return self.type + ": " + str(self.amount) + " " + self.cname + " (" + self.ename + ")"
class MudNpc(object):
    def __init__(self):
        self.ename = ""
        self.cname = ""
        self.type = ""
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
def func_hpbrief_update(line):    
    p = re.compile(r'^#(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
    m = p.match(line)
    if m is not None:
        status = (int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))
        mystatus.update_hpbrief(status)

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

    keep=True
    while keep:
        sleep(0.3)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                keep=False

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
        
        # draw room name
        room_name_font = pygame.font.Font('simhei.ttf', 20)
        screen.blit(drawText(current_room.cname,room_name_font),(cfg_gui.room_desc_rec[0] + cfg_gui.room_desc_rec[2]/2 - 50 ,cfg_gui.room_desc_rec[1] - 30))
        # draw room desc
        fontName = 'simhei.ttf'
        content = current_room.desc        
        drawMultilineText(screen,content,fontName,cfg_gui.room_desc_rec,line_space=5)
        # draw room items and npcs
        item_rows = int(math.ceil(len(current_room.items)/3.0))
        for i in range(item_rows):
            for j in range(3):                
                if 3*i + j < len(current_room.items):
                    screen.blit(game_images['itembg'],(cfg_gui.room_items_rec[0]+j*170,cfg_gui.room_items_rec[1]+i*25))
                    icon = game_images['unknown']
                    if current_room.items[3*i + j].type=="food":
                        icon = game_images['food']
                    if current_room.items[3*i + j].type=="drink":
                        icon = game_images['drink'] 
                    #draw icon
                    screen.blit(icon,(cfg_gui.room_items_rec[0]+j*170+2,cfg_gui.room_items_rec[1]+i*25))
                    #draw text
                    item_font = pygame.font.Font('simhei.ttf', 14)
                    content = str(current_room.items[3*i + j].amount) + " " + current_room.items[3*i + j].cname + "(" + current_room.items[3*i + j].ename + ")"
                    screen.blit(drawText(content,item_font,color=(64,64,64)),(cfg_gui.room_items_rec[0]+j*170+25,cfg_gui.room_items_rec[1]+i*25+2))
        npcs_per_row = 2
        npc_rows = int(math.ceil(len(current_room.npcs)/(npcs_per_row+0.0)))
        room_npcs_rec = (cfg_gui.room_items_rec[0],cfg_gui.room_items_rec[1] + item_rows*25,cfg_gui.room_items_rec[2],cfg_gui.room_items_rec[3])
        for i in range(npc_rows):
            for j in range(npcs_per_row):                
                if npcs_per_row*i + j < len(current_room.npcs):
                    screen.blit(game_images['npcbg'],(room_npcs_rec[0]+j*260,room_npcs_rec[1]+i*25))
                    icon = game_images['npc']                    
                    #draw icon
                    screen.blit(icon,(room_npcs_rec[0]+j*260+2,room_npcs_rec[1]+i*25))
                    #draw text
                    npc_font = pygame.font.Font('simhei.ttf', 14)
                    content = current_room.npcs[npcs_per_row*i + j].format(19)
                    screen.blit(drawText(content,npc_font,color=(64,64,64)),(room_npcs_rec[0]+j*260+25,room_npcs_rec[1]+i*25+2))
       


        pygame.display.update()
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