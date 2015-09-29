#-*- coding: UTF-8 -*-
#!/usr/bin/env python

import sys
import wx
import Window
import xlwt 
def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    #testexcel()
    app = wx.App()
    frame = Window.Window()
    frame.Show()
    app.MainLoop()
    #extractor = wikiextractor()  
    #extractor.parse_members(sys.argv[1], 'f')
    
def testexcel():
    wbk =xlwt.Workbook() 
    sheet =wbk.add_sheet('sheet 1')
    sheet.write(0,1,'中文'.decode('utf8'))
    wbk.save('test.xls')
    
if __name__ == '__main__':
    main()
