# -*- coding: utf-8 -*-

import pygame
import cfg_gui
 
class TextBox:
    def __init__(self,rect, font=None,font_color= (255, 255, 255),callback=None):
        """
        :param rect:文本框rect
        :param font:文本框中使用的字体
        :param callback:在文本框按下回车键之后的回调函数
        """
        self.width = rect.width
        self.height = rect.height
        self.left = rect.left
        self.top = rect.top
        self.text = ""  # 文本框内容
        self.font_color = font_color
        self.callback = callback
       
        if font is None:
            self.font = pygame.font.Font(None, 16)  # 使用pygame自带字体
        else:
            self.font = font

        self.focused = False
 
    def draw(self, screen):
        #don't let text out of the box
        if self.font.size(self.text)>self.width:
            clopIndex = len(self.text)
            for i in range(len(self.text)):
                if self.font.size(self.text[:i+1])[0] > self.width:
                    clopIndex = i
                    break
            self.text = self.text[:clopIndex]


        text_surf = self.font.render(self.text, True, self.font_color)        
        screen.blit(text_surf, (self.left,self.top))
        #draw a flash _ after text
        if self.focused:
            cmd_flash_img = pygame.image.load(cfg_gui.IMAGE_PATHS['cmd_flash'])
            screen.blit(cmd_flash_img,(self.left+text_surf.get_width()+1,self.top))
 
    def key_down(self, event):
        if not self.focused:
            return
        try:
            unicode = event.unicode
            key = event.key
    
            # 退位键
            if key == 8 and len(self.text)>0:
                self.text = self.text[:-1]
                return
    
            # 切换大小写键
            if key == 301:
                return
    
            # 回车键
            if key == 13:
                if self.callback is not None:
                    self.invokeCallback()
                return
    
            if unicode != "":
                char = unicode
            else:
                char = chr(key)
    
            self.text += char
        except Exception as e:
            print "invalid input char"
 
 
    def invokeCallback(self):
        self.callback(self.text)
