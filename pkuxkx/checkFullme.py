# -*- coding: utf-8 -*-
import sys
import pdb
import os
import re
import urllib2
import io

def main(args):
    resp = urllib2.urlopen(urllib2.Request("http://tensor.applinzi.com/checkFullme"))
    content = resp.read()
    print content.decode("utf8").encode("gb18030")   
    
       
if __name__=="__main__":
    main(sys.argv)
