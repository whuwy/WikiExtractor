#-*- coding: UTF-8 -*-
#!/usr/bin/env python

import sys
import wx
import Window
import xlwt 
def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = wx.App()
    frame = Window.Window()
    frame.SetMaxSize((550,670))
    frame.Show()
    app.MainLoop()
    #extractor = wikiextractor()  
    #extractor.parse_members(sys.argv[1], 'f')
    
if __name__ == '__main__':
    main()
