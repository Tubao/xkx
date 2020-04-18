# -*- coding: utf-8 -*-

'''config file'''
import os
import pygame


# FPS
FPS = 100
# 屏幕大小
SCREENSIZE = (800, 700)
# room desc rect
room_desc_rec = (10,90,500,200)
# room items rec
room_items_rec = (10,300,500,100)
# action buttons rec
action_area_rec = (10,500,500,100)
# command_line rec
command_line_rec = (10,580,300,50)
# terminal-like rec
twindows_rec = (10,50,500,520)
twindows_rec1 = (10,50,500,300)
twindows_rec2 = (10,380,500,190)
twindows_rec3 = (512,50,500,520)
# gps area rec
gps_rec = (520,55,280,300)
# direction area rec
direction_rec = (540,300,240,240)

#direction rec dict
direction_rec_dict = {
    "northwest":pygame.Rect(0,0,72,72),
    "northeast":pygame.Rect(168,0,72,72),
    "southwest":pygame.Rect(0,168,72,72),
    "southeast":pygame.Rect(168,168,72,72),
    "up":pygame.Rect(84,84,72,30),
    "down":pygame.Rect(84,124,72,30),
    "northup":pygame.Rect(84,0,72,22),
    "north":pygame.Rect(84,24,72,22),
    "northdown":pygame.Rect(84,50,72,22),
    "southdown":pygame.Rect(84,168,72,22),
    "south":pygame.Rect(84,192,72,22),
    "southup":pygame.Rect(84,216,72,22),
    "westup":pygame.Rect(0,84,22,72),
    "west":pygame.Rect(24,84,22,72),
    "westdown":pygame.Rect(50,84,22,72),
    "eastdown":pygame.Rect(168,84,22,72),
    "east":pygame.Rect(192,84,22,72),
    "eastup":pygame.Rect(216,84,22,72)
}


# 图片路径
IMAGE_PATHS = {
                'rabbit': os.path.join(os.path.dirname(__file__), 'resources/images/dude.png'),
                'grass': os.path.join(os.path.dirname(__file__), 'resources/images/grass.png'),
                'castle': os.path.join(os.path.dirname(__file__), 'resources/images/castle.png'),
                'arrow': os.path.join(os.path.dirname(__file__), 'resources/images/bullet.png'),
                'badguy': os.path.join(os.path.dirname(__file__), 'resources/images/badguy.png'),
                'healthbar': os.path.join(os.path.dirname(__file__), 'resources/images/healthbar_edited.png'),
                'health': os.path.join(os.path.dirname(__file__), 'resources/images/health_edited.png'),
                'gameover': os.path.join(os.path.dirname(__file__), 'resources/images/gameover.png'),
                'youwin': os.path.join(os.path.dirname(__file__), 'resources/images/youwin.png'),
                'split1': os.path.join(os.path.dirname(__file__), 'resources/images/timg_edited2.png'),
                'split2': os.path.join(os.path.dirname(__file__), 'resources/images/split2_edited.png'),
                'itembg': os.path.join(os.path.dirname(__file__), 'resources/images/itembg_edited.png'),
                'npcbg': os.path.join(os.path.dirname(__file__), 'resources/images/npcbg_edited.png'),
                'food': os.path.join(os.path.dirname(__file__), 'resources/images/food_edited.png'),
                'drink': os.path.join(os.path.dirname(__file__), 'resources/images/drink_edited.png'),
                'npc': os.path.join(os.path.dirname(__file__), 'resources/images/npc_edited.png'),
                'unknown': os.path.join(os.path.dirname(__file__), 'resources/images/unknown_edited.png'),
                'action_button_bg1': os.path.join(os.path.dirname(__file__), 'resources/images/action_button_bg1.png'),
                'action_button_bg2': os.path.join(os.path.dirname(__file__), 'resources/images/action_button_bg2.png'),
                'cmdline_icon': os.path.join(os.path.dirname(__file__), 'resources/images/cmdline_icon.png'),
                'cmdline': os.path.join(os.path.dirname(__file__), 'resources/images/cmdline.png'),
                'cmdline_bt': os.path.join(os.path.dirname(__file__), 'resources/images/cmdline_bt.png'),
                'cmd_flash': os.path.join(os.path.dirname(__file__), 'resources/images/cmd_flash.gif'),
                'checked': os.path.join(os.path.dirname(__file__), 'resources/images/checked.png'),
                'unchecked': os.path.join(os.path.dirname(__file__), 'resources/images/unchecked.png'),
                'cmd_window': os.path.join(os.path.dirname(__file__), 'resources/images/cmd_window_edited.jpeg'),
                'direction_bg': os.path.join(os.path.dirname(__file__), 'resources/images/direction.png')                 
                
            }
# 游戏声音路径
SOUNDS_PATHS = {
                'hit': os.path.join(os.path.dirname(__file__), 'resources/audio/explode.wav'),
                'enemy': os.path.join(os.path.dirname(__file__), 'resources/audio/enemy.wav'),
                'shoot': os.path.join(os.path.dirname(__file__), 'resources/audio/shoot.wav'),
                'moonlight': os.path.join(os.path.dirname(__file__), 'resources/audio/moonlight.wav')
            }

itemInRoom_buttonMsg_dict = {
    'food':['get','get all','look','eat','drop'],
    'drink':['get','get all','look','drink','drop'],
    'other':['get','get all','drop','look','fight','hit','kill'],
    'npc':['look','fight','hit','kill']
}


