#-*- coding: UTF-8 -*-
import xml.sax.handler
import Extractor
import logging.handlers
import threading
import codecs
import configuration
import csv
from FileWriter import filewriter

class LocalExtractorThread(threading.Thread):     
    def __init__(self, infile, statusbar,localextractbtn,stoplocalextractbtn):
        threading.Thread.__init__(self)            
        self.thread_stop = False
        self.statusbar = statusbar
        self.infile = infile
        self.indexfile=open("wikipedia-data.csv",'wb')
        #重要，实现中文字符写入
        self.indexfile.write(codecs.BOM_UTF8)
        #2015年10月31日14:45:44，使用#作为分隔符
        self.indexfile.writelines("id#文章名称#经度#纬度#链接\n".encode())
        self.indexfile.flush()
        self.filewriter = filewriter()
        self.instancelogger()
        self.startextractbtn=localextractbtn
        self.stopextractbtn=stoplocalextractbtn
        
    def run(self): #Overwrite run() method, put what you want the thread do here  
        self.startextractbtn.Enable(False)
        self.stopextractbtn.Enable(True)
        self.Parse(self.infile,self.statusbar)   
        self.startextractbtn.Enable(True)
        self.stopextractbtn.Enable(False)
                
    def stop(self):  
        self.thread_stop = True
        self.startextractbtn.Enable(True)
        self.stopextractbtn.Enable(False)
        
    def Parse(self,infile,statusbar):
        parser = xml.sax.make_parser()
        handler = LocalExtractorHandler(statusbar,self.indexfile,self.filewriter,self.logger)
        handler.setExtractThread(self)
        parser.setContentHandler(handler)
        parser.parse(infile)
        self.indexfile.close()
        success = u'全部网页解析完毕!'
        print success
        self.logger.info(success)
        self.statusbar.SetStatusText(success)
        
    def instancelogger(self):
        LOG_FILE = 'extractor.log'
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # ʵ����handler 
        fmt = '%(asctime)s - %(filename)s:%(lineno)s  - %(message)s'
        
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('extractor')  
        self.logger.addHandler(handler)     
        self.logger.setLevel(logging.DEBUG)
                 
class LocalExtractorHandler(xml.sax.handler.ContentHandler):
    def __init__(self,statusbar,indexfile,filewriter,logger):
        self.inTitle = False 
        self.inText = False
        self.inID = False
        self.OutRevision = True
        self.text =""
        self.title=""
        self.id=""
        self.wikiextractor = Extractor.wikiextractor()
        self.statusbar = statusbar
        self.indexfile=indexfile
        self.filewriter = filewriter
        self.logger=logger
        #读取文件
        with open('F:\\wiki\\i.csv') as f:
            d_csv = csv.DictReader(f)
            self.dict = []
            for row in d_csv:
                 self.dict.append(row['name'].decode("utf8"))

    def setExtractThread(self,extractthread):
        self.extractthread = extractthread
            
    def startElement(self, name, attributes):
        if self.extractthread.thread_stop: 
            return
        
        if name == "text": 
            self.inText =True 
            self.text =""
        elif name == "title":
            self.inTitle = True 
            self.title=""
        elif name == "revision":
            self.OutRevision = False 
        elif name == "id" and self.OutRevision:
            self.inID=True;
            self.id = ""
    def characters(self, data):
        if self.extractthread.thread_stop: 
            return
        if self.inTitle:
            self.title += data
        if self.inText:
            self.text += data
        if self.inID:
            self.id += data
    def endElement(self, name):
        if self.extractthread.thread_stop: 
            return
        
        if name == "title":
            self.inTitle = False            
        if name == "text":
            self.inText =False            
            try:
                #判断是否在字典中
                if self.title not in self.dict:
                    info = u'忽略ID为{0}的\"{1}\"'.format(self.id,self.title)
                    #状态栏中显示
                    self.statusbar.SetStatusText(info)
                    return
                data=self.wikiextractor.parsecontentfromxml(self.text,self.id,self.title)
                #保存模板信息和信息框信息
                info = u'成功解析ID为{0}的\"{1}\"'.format(self.id,self.title)
                self.filewriter.SaveToJSON(data,self.title)
                #日志中记录
                #self.logger.info(info)
                #状态栏中显示
                self.statusbar.SetStatusText(info)                    
            except Exception,e:
                error = u'ID为{0}的页面\"{1}\"解析失败'.format(self.id,self.title)
                self.logger.error(error)
                self.statusbar.SetStatusText(error)
                return       
        if name == "id":
            self.inID =False   
        if name == "revision":
            self.OutRevision = True
            