#-*- coding: UTF-8 -*-
#!/usr/bin/env python

import wx,sys
import webbrowser
import configuration,Extractor,FileWriter
import LocalExtractorHandler
import os

class Window (wx.Frame):
    def __init__(self):        
        wx.Frame.__init__(self, None, -1,
                          u"维基百科信息抽取工具",
                          size=(550,670))
        notebook = wx.Notebook(self) 
        attrpanel = wx.Panel(notebook)              
        notebook.AddPage(attrpanel,u"在线抽取")
        localpanel = wx.Panel(notebook)              
        notebook.AddPage(localpanel,u"本地抽取")
       
        #############################################
        #attrpanel面板界面
        # mainSizer 自上往下，管理整个框架
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        #搜索行
        categorylbl = wx.StaticText(attrpanel, -1, u"请输入要查询的类:")
        self.categoryname = wx.TextCtrl(attrpanel, -1, "",size=(200,-1));
        self.searchbtn = wx.Button(attrpanel, -1, u"查询")
        self.searchpreck = wx.CheckBox(attrpanel,-1,u"前缀查询") 
        self.Bind(wx.EVT_BUTTON, self.OnSearch, self.searchbtn)
        
        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        searchSizer.Add(categorylbl, 0,  wx.ALIGN_LEFT)
        searchSizer.Add(self.categoryname)
        searchSizer.Add(self.searchbtn)
        searchSizer.Add(self.searchpreck)
        
        searchSizer.Add(wx.StaticLine(attrpanel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(searchSizer,0,wx.EXPAND|wx.ALL,10)
        
        #子类结果行
        subcategoryresultSizer = wx.BoxSizer(wx.VERTICAL)        
        subcategoryresultlbl = wx.StaticText(attrpanel, -1, u"子类查询结果:")
        self.subcategoryresultlist = wx.ListCtrl(attrpanel, -1, style=wx.LC_REPORT,size=(500,200))
        self.subcategoryresultlist.InsertColumn(0,u"类名")
        self.subcategoryresultlist.SetColumnWidth(0, 500);
        # 双击响应函数
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCategoryItemActivated, self.subcategoryresultlist)
        
        subcategoryresultSizer.Add(subcategoryresultlbl, 0,  wx.ALIGN_TOP)
        subcategoryresultSizer.Add(self.subcategoryresultlist)
        
        self.mainSizer.Add(subcategoryresultSizer,0,wx.EXPAND|wx.ALL,10)
        
        #页面结果行
        pageresultSizer = wx.BoxSizer(wx.VERTICAL)        
        pageresultlbl = wx.StaticText(attrpanel, -1, u"页面查询结果:")
        self.pageresultlist = wx.ListCtrl(attrpanel, -1, style=wx.LC_REPORT,size=(500,200))
        self.pageresultlist.InsertColumn(0,u"pageid")
        self.pageresultlist.InsertColumn(1,u"文章名")
        self.pageresultlist.SetColumnWidth(0, 80);
        self.pageresultlist.SetColumnWidth(1, 420);
        # 双击响应函数
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPageItemActivated, self.pageresultlist)
        
        pageresultSizer.Add(pageresultlbl, 0,  wx.ALIGN_TOP)
        pageresultSizer.Add(self.pageresultlist)
        
        self.mainSizer.Add(pageresultSizer,0,wx.EXPAND|wx.ALL,10)
        
        #按钮行
        self.extractbtn = wx.Button(attrpanel, -1, u"执行抽取")
        self.Bind(wx.EVT_BUTTON, self.OnExtract, self.extractbtn)
        self.extractsubcategoryck = wx.CheckBox(attrpanel,-1,u"抽取子类页面")         
        extractSizer = wx.BoxSizer(wx.HORIZONTAL)
        extractSizer.Add(self.extractbtn, 0,  wx.ALIGN_LEFT)
        extractSizer.Add(self.extractsubcategoryck)
        
        self.mainSizer.Add(extractSizer,0,wx.EXPAND|wx.ALL,10)
        
        attrpanel.SetSizer(self.mainSizer)
        #mainSizer.Fit(self)
        #self.SetMinSize(self.GetSize())
    
        #############################################
        #本地抽取面板
        self.localpanelSizer = wx.BoxSizer(wx.VERTICAL)
        #输入文件路径        
        infilelbl = wx.StaticText(localpanel, -1, u"请选择 xml所在路径:  ")
        self.infiletxt = wx.TextCtrl(localpanel, -1, "",size=(300,-1));
        self.infilebtn = wx.Button(localpanel, -1, u"选择")
        self.Bind(wx.EVT_BUTTON, self.OnInFile, self.infilebtn)
        
        fileSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileSizer.Add(infilelbl, 0,  wx.ALIGN_LEFT)
        fileSizer.Add(self.infiletxt)
        fileSizer.Add(self.infilebtn)        
        self.localpanelSizer.Add(fileSizer,0,wx.EXPAND|wx.ALL,10)

        #输出文件路径        
        outpathlbl = wx.StaticText(localpanel, -1, u"请选择解析输出路径:  ")
        self.outpathtxt = wx.TextCtrl(localpanel, -1, "",size=(300,-1));
        self.outpathbtn = wx.Button(localpanel, -1, u"选择")
        self.Bind(wx.EVT_BUTTON, self.OnOutFile, self.outpathbtn)
        
        fileSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileSizer.Add(outpathlbl, 0,  wx.ALIGN_LEFT)
        fileSizer.Add(self.outpathtxt)
        fileSizer.Add(self.outpathbtn)        
        self.localpanelSizer.Add(fileSizer,0,wx.EXPAND|wx.ALL,10)
        
        fileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.localextractbtn = wx.Button(localpanel,-1,u"开始抽取")
        self.Bind(wx.EVT_BUTTON, self.OnLocalExtract, self.localextractbtn)
        fileSizer.Add(self.localextractbtn,0,wx.ALIGN_LEFT)
        self.stoplocalextractbtn = wx.Button(localpanel,1,u"停止抽取")
        self.Bind(wx.EVT_BUTTON, self.OnStopLocalExtract, self.stoplocalextractbtn)
        fileSizer.Add(self.stoplocalextractbtn,0,wx.ALIGN_RIGHT)
        self.stoplocalextractbtn.Enable(False)
        
        self.localpanelSizer.Add(fileSizer,0,wx.EXPAND|wx.ALL,10)

        
        localpanel.SetSizer(self.localpanelSizer)
        #状态栏
        self.statusbar = self.CreateStatusBar()  
        
        #############################################
        self.resultdict = {}
        self.outpath=""
        self.infile=""
        self.parserthread=None
        
    def OnOutFile(self,evt):
        #创建标准文件对话框
        dialog = wx.DirDialog(self,u"打开路径...",style=wx.OPEN)
        #这里有个概念：模态对话框和非模态对话框. 它们主要的差别在于模态对话框会阻塞其它事件的响应,
        #而非模态对话框显示时,还可以进行其它的操作. 此处是模态对话框显示. 其返回值有wx.ID_OK,wx.ID_CANEL;
        if dialog.ShowModal() == wx.ID_OK:
            self.outpathtxt.SetValue(dialog.GetPath())
            self.outpath=dialog.GetPath()
            #销毁对话框,释放资源.
            dialog.Destroy() 
                
    def OnInFile(self,evt):
        #创建标准文件对话框
        dialog = wx.FileDialog(self,u"打开文件...",style=wx.OPEN,wildcard=u"xml文件|*.xml|所有文件|*.*")
        #这里有个概念：模态对话框和非模态对话框. 它们主要的差别在于模态对话框会阻塞其它事件的响应,
        #而非模态对话框显示时,还可以进行其它的操作. 此处是模态对话框显示. 其返回值有wx.ID_OK,wx.ID_CANEL;
        if dialog.ShowModal() == wx.ID_OK:
            self.infiletxt.SetValue(dialog.GetPath())
            self.infile=dialog.GetPath()
            #销毁对话框,释放资源.
            dialog.Destroy()
            
      
    def OnLocalExtract(self,evt):
        #改变当前路径
        if os.path.exists(self.outpath) :
            os.chdir(self.outpath)
        #开启新线程
        self.parserthread = LocalExtractorHandler.LocalExtractorThread(self.infile,self.statusbar,self.localextractbtn,self.stoplocalextractbtn)
        self.parserthread.start()
        
    def OnStopLocalExtract(self,evt):
        if self.parserthread :
            self.parserthread.stop()
        self.statusbar.SetStatusText(u"停止解析文件...")
        
    def OnSearch(self,evt):
        if self.searchinpageck.Get3StateValue() == wx.CHK_CHECKED:
            self.SearchbyPrex(self.categoryname.GetValue())
        else:
            self.SearchCategorymember(self.categoryname.GetValue())     
         
    def OnExtract(self,evt):
        try:
                categoryname = self.categoryname.GetValue()
                wikiextractor = Extractor.wikiextractor()
                data_dict = {}
                if self.extractsubcategoryck.Get3StateValue() == wx.CHK_CHECKED:
                    wikiextractor.parse_members(categoryname, data_dict,'t')
                else:
                    wikiextractor.parse_members(categoryname, data_dict,'f')
                filewriter=FileWriter.filewriter()
                #filewriter.SaveToSQLite(data_dict)
                filewriter.SaveToExcel(data_dict)
                self.statusbar.SetStatusText(u"保存成功，请检查excel文件",0)
        except Exception,e:            
            self.statusbar.SetStatusText(e.message,0) 
      
    def SearchbyPrex(self,prex):
        try:
            self.subcategoryresultlist.DeleteAllItems();
                        
            wikiextractor = Extractor.wikiextractor()
            query = configuration.api_url_zh + '&list=allcategories&acprefix=%s'% prex
            json_content = wikiextractor.getjson(query)
            members = json_content['query']['allcategories']
            
            for member in members:
                #TODO:如果没有Category属性,无法判断是否为子类(?)
                category = member['*']  
                index = self.subcategoryresultlist.InsertStringItem(sys.maxint, category)
                self.subcategoryresultlist.SetStringItem(index, 0, category)    
        except Exception,e:            
            self.statusbar.SetStatusText(e.message,0)    

    def SearchCategorymember(self,categoryname):
        try:
            self.subcategoryresultlist.DeleteAllItems();
            self.pageresultlist.DeleteAllItems();
            wikiextractor = Extractor.wikiextractor()
            query = configuration.api_url_zh +'&list=categorymembers&cmtitle=Category:%s&cmsort=timestamp&' \
                'cmdir=desc&cmlimit=max' % categoryname
            json_content = wikiextractor.getjson(query)
            
            members = json_content['query']['categorymembers']
            
            for member in members:
                #TODO:如果没有Category属性,无法判断是否为子类(?)
                pageid = str(member['pageid'])
                
                if 'Category:' in member['title']:                    
                    subcategory = member['title'].lstrip('Category:')
                    index = self.subcategoryresultlist.InsertStringItem(sys.maxint, subcategory)
                    self.subcategoryresultlist.SetStringItem(index, 0, subcategory)                     
                else:
                    page = member['title']
                    #TODO:待完善
                    # 说明不是有效的page
                    if ':' in page:
                        continue
                    
                    index = self.pageresultlist.InsertStringItem(sys.maxint, pageid)
                    self.pageresultlist.SetStringItem(index, 0, pageid)
                    self.pageresultlist.SetStringItem(index, 1, page)     
        except Exception,e:
            self.statusbar.SetStatusText(e.message,0)
        
    def OnCategoryItemActivated(self, evt):
        item = evt.GetItem()
        category = item.GetText()        
        #查询子类
        self.SearchCategorymember(category)
        #修改当前查询类名
        self.categoryname.SetValue(category)
        
    def OnPageItemActivated(self, evt):
        index = evt.GetIndex()
        article = self.pageresultlist.GetItem(index, 1).GetText()
        #打开新窗口
        url = configuration.base_url_zh+article
        webbrowser.open_new_tab(url)  
    
