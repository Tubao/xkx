# -*- coding: utf-8 -*-
import sys
import pdb
import os
import re
import urllib2
import io

def main(args):
    url = "http://pkuxkx.net/antirobot/robot.php?filename=" + args[1].decode("gb18030").encode("utf8")
#    url = "http://pkuxkx.net/antirobot/robot.php?filename=" + str(1501885219595216)
    
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    content = resp.read()
    
    s = re.search(r'b2evo_captcha_tmp/(.*?).jpg',content)
    fid = s.group(1)
    r = urllib2.urlopen(urllib2.Request("http://tensor.applinzi.com/setFullme?id="+fid))
    
    
       
if __name__=="__main__":
    main(sys.argv)
