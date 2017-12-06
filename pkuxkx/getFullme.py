# -*- coding: utf-8 -*-
import sys
import pdb
import os
import re
import urllib2
from PIL import Image
import io

def main(args):
    url = r"http://pkuxkx.net/antirobot/robot.php?filename=" + args[1].decode("gb18030").encode("utf8")
#    url = "http://pkuxkx.net/antirobot/robot.php?filename=" + str(150180061498858)
    
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    content = resp.read()
    print url
    print content
    s = re.search(r'b2evo_captcha_tmp/(.*?).jpg',content)
    fid = s.group(1)
    img_url = "http://pkuxkx.net/antirobot/b2evo_captcha_tmp/" + fid + ".jpg"
    image_file = io.BytesIO(urllib2.urlopen(img_url).read())
    img = Image.open(image_file)
    img.show()
   
    
       
if __name__=="__main__":
    main(sys.argv)
