#-*- coding: UTF-8 -*-
#!/usr/bin/env python

import sys
import os
import re
import requests
import codecs
import configuration
from FileWriter import filewriter

# Allow unicode characters to be printed.
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
#api_url = 'http://zh.wikipedia.org/w/api.php?action=query&format=json'

class wikiextractor():
    def __init__(self):
        self.infoboxschemal = {}
        #self.clear_db()
        self.currentpageid=0
        self.currentarticlename=""
        
    #def clear_db(self):
        #scraperwiki.sql.execute("drop database main;")

        #scraperwiki.sql.commit()
        #if os.path.isfile("scraperwiki.sqlite"):
        #    os.remove("scraperwiki.sqlite")
        #    scraperwiki.sql.commit()
            
    def clean_data(self,data):
        # Strip square brackets.
        data = re.sub('[\[\]]', '', data)
        # Strip all HTML tags.
        data = re.sub('<[^<]+?>', ' ', data)
        # 移除所有{{}}对象
        data = re.sub('(?i)\{\{.*\}\}', '', data)
        data = re.sub('&nbsp;', '', data)        
        return data
    
    def clean_data_with_text(self,data):
        # Strip square brackets.
        data = re.sub('\[\[.*\]\]', '', data)
        # Strip all HTML tags.
        data = data.replace('<!--', '' )
        data = data.replace('-->', '' )
        data = re.sub(u'\(.*\)', '',data)
        data = data.replace('&nbsp;', '')
        return data
    
    
    def parse_tags(self,data):
        data = re.sub('(?i)\{\{url\|([^\n]*)\}\}', '\g<1>', data)
        data = re.sub('\[\[(.*)\|.*\]\]', '\g<1>', data)
        data = re.sub('(?i)\{\{convert\|(.*?)\|(.*?)((\}\})|(\|.*\}\}))', '\g<1> \g<2>', data)
        data = re.sub('(?i)\{\{convinfobox\|(.*?)\|(.*?)((\}\})|(\|.*\}\}))', '\g<1> \g<2>', data)
        data = re.sub('(?i)\{\{nowrap\|(.*)\}\}', '\g<1>', data)
        return data
    
    #解析catagory类下所有的对象，如果include_subcat为true，继续解析其子类对象
    def parse_members(self,category, data_dict, include_subcat='f'):
            category = category.replace(' ', '_')        
            try:
                query = configuration.api_url_zh +'&list=categorymembers&cmtitle=Category:%s&cmsort=timestamp&' \
                    'cmdir=desc&cmlimit=max' % category
                json_content = self.getjson(query)
                members = json_content['query']['categorymembers']
                self.get_data_dict(members, data_dict, include_subcat)                                            
            except Exception,e:
                raise Exception(e)
            
    #根据页面ID获取并解析其对应的信息
    def get_data_dict_from_pageid(self, pageidlist, data_dict,include_subcat='f'):        
        for page in pageidlist:
            data = self.parsecontent(page)    
            if data is not None:
                #按照infobox的名称分别管理
                for tablename in data.keys():
                    tabledata = data[tablename]
                    if tablename in data_dict.keys():
                        if len(tabledata) > 2:
                            data_dict[tablename].append(tabledata)
                    else:                         
                        if len(tabledata) > 2:
                            data_list = []
                            data_list.append(tabledata)
                            data_dict[tablename] = data_list
                            
    #从成员列表解析器对应的信息内容，存储在data_dict中
    def get_data_dict(self, members, data_dict,  include_subcat='f'):
        pages = []
        subcategories = []
        for member in members:
            #TODO:对于子类的判断需要完善，如果不包含Category？
            if 'Category:' in member['title']:
                if include_subcat == 't':
                    subcategory = member['title'].lstrip('Category:')
                    subcategories.append(subcategory)
            else:
                pages.append(member['pageid'])
                
        self.get_data_dict_from_pageid(pages,data_dict,include_subcat)
                        
         #分类
        for subcategory in subcategories:
            subcategory = subcategory.replace('Category:', '')
            self.parse_members(subcategory, data_dict, include_subcat )
                

    def getjson(self,url):
        #首先登陆
        if 0:
            try:
                #r = requests.post("https://en.wikipedia.org/w/api.php?action=query&format=json&meta=tokens&type=login&lgname=lixiangboss")
                #tokenjson  = r.json()
                #token = tokenjson["query"]["tokens"]["logintoken"]
                #postdata = {'lgname':'lixiangboss','lgpassword':'chxylx','lgtoken':'48b34365bb2576ded3e821cf67d729f2590fefdd+\\'}
                postdata = {'name':'lixiangboss','password':'chxylx','token':'48b34365bb2576ded3e821cf67d729f2590fefdd+\\'}
                token='48b34365bb2576ded3e821cf67d729f2590fefdd+\\'
                loginurl = "https://en.wikipedia.org/w/api.php?action=query&meta=tokens&type=login&format=json"
                l = requests.post(loginurl, data=postdata)
                print l.text
                loginjson  = l.json()
                loginresult=loginjson["login"]["result"]
                
            except Exception,e:
                raise Exception(u'尝试登陆失败，请检查用户名')   
                      
        try:
            #定制请求头
            #headers = {'user_agent':'WikiExtrator/1.1 (http://www.geodatamining.cn/; whuwy@163.com) BasedOnPython/1.4'}
            headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding':'gzip, deflate, sdch, br',
                       'Accept-Language':'zh-CN,zh;q=0.8',
                        'Cache-Control':'max-age=0',
                        'Connection':'keep-alive',
                        'Cookie':'WMF-Last-Access=08-May-2017; WMF-Last-Access-Global=08-May-2017; GeoIP=US:CA:Mountain_View:37.42:-122.06:v4; TBLkisOn=0',
                        'Host':'zh.wikipedia.org',
                        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
            request = requests.get(url, headers=headers)
            json_content = request.json()
            return json_content
        except Exception,e:
            #print e.message
            #print repr(e)
            raise Exception(u'网络连接失败，请检查')   
          
    def parsecontentfromxml(self,content,pageid,article_name):
        try:            
            #data结构:{tablename,{columnname,value}}
            data = {}
            data['id'] = pageid
            data['article_name'] = article_name       
            self.parse_coord(content,data)
            #暂时只解析地理坐标，先不解析信息框和模板
            #2015-12-14 19:53:22，时代在变，代码也要于是俱进，开始解析信息框和模板了
            self.parse_infobox(content,data)
            self.parse_template(content,data)
            return data
        except Exception,e:
            raise e       
     
    def parsecontent(self,pageid,shemal=False):        
        try:
            query = configuration.api_url_zh + '&action=query&pageids=%s&prop=revisions&rvprop=content' % pageid
            json_content = self.getjson(query)
            
            pageid = json_content['query']['pages'].keys()[0]
            content = json_content['query']['pages'][pageid]['revisions'][0]['*']
            article_name = json_content['query']['pages'][pageid]['title']
        
            # Remove HTML comment tags.
            content = re.sub('<!--[\\S\\s]*?-->', ' ', content)
            #检查是否包含非法字符（如|、:等）
            #m = re.match(u'[^a-zA-Z0-9\u4E00-\u9FA5]', article_name)
            #if m:
            if ':' in article_name:
                return 
            #data结构:{tablename,{columnname,value}}閿熺粨鏋�            
            data = {}
            self.currentpageid =  pageid
            self.currentarticlename = article_name
           
            #self.parse_province(content,data)
            self.parse_coord(content,data)
            self.parse_infobox(content,data)
            
            return data
        except Exception,e:
            raise e
            
  
    #解析坐标信息
    #TODO,有bug，待完善
    def parse_coord_old(self,content,data):
        
        tabledata = {}
        if self.currentpageid != 0:
            tabledata['id'] = self.currentpageid
            tabledata['article_name'] = self.currentarticlename
        
        coord_occurences = re.findall('{{coord.*}}', content, re.U)
        
        for coord_occurence in coord_occurences:
    
            coords = re.findall('(\|\d{2,3}){3,4}\|[WESN]', coord_occurence,re.U)
            for coord in coords:
                if coord[-1].lower()=='n' or coord[-1].lower()=='s':
                 tabledata["lat"] = coord
                if coord[-1].lower()=='e' or coord[-1].lower()=='w':
                 tabledata["lon"] = coord    
        data["Coord"] = tabledata
    
    #解析坐标信息
    def parse_coord(self,content,data):
        
        tabledata = {}                
        #查找{{coord|...|display=title}}字符
        coords = re.findall('{{coord.*display=title.*}}', content.lower())
        if len(coords)>0:
            coordtext=coords[0]        
            #替换空格
            coordtext=coordtext.replace(' ','')
            #注意：将两个||替换为一个|,否则会报错
            coordtext=coordtext.replace('||','|')                
            #是否包含经纬度标识
            marks = re.findall('\|[wens]\|', coordtext)
            if len(marks)>0:
                #注意，利用最外层的括号来获取完整匹配结果
                locations = re.findall('(\|-?\d{1,3}[.]?\d{0,13}(\|\d{1,3}[.]?\d{0,13}){0,2}\|[wens])', coordtext)                    
                if len(locations)!=2:
                    return
                
                #注意，使用括号匹配时的返回结果！
                lattext = locations[0][0]
                lontext = locations[1][0]
                
                lattext = re.split('\|[wens]', lattext)[0]
                lontext = re.split('\|[wens]', lontext)[0]
                #纯数字            
                lattext=lattext.strip('|')                    
                lontext=lontext.strip('|')                    
                #分割数字        
                lat=re.split('\|',lattext)
                lon=re.split('\|',lontext)
                
                latnum=float(lat[0])
                if len(lat)==2:
                    latnum=latnum+float(lat[1])/60.0
                if len(lat)==3:
                    latnum=latnum+float(lat[1])/60.0 + float(lat[2])/3600.0
                    
                lonnum=float(lon[0])
                if len(lon)==2:
                    lonnum=lonnum+float(lon[1])/60.0
                if len(lon)==3:
                    lonnum=lonnum+float(lon[1])/60.0 + float(lon[2])/3600.0        
                
                #判断东西经度，南北纬度
                southindex =coordtext.find('|s|')
                westhindex =coordtext.find('|w|')
                if southindex>0:
                    latnum=0-latnum
                if westhindex>0:
                    lonnum=0-lonnum
            else:
                #此时，经纬度用小数点表示，不进行|划分
                locations = re.findall('\|-?\d{1,3}[.]?\d{0,13}', coordtext)                    
                if len(locations)!=2:
                    return    
                
                lattext = locations[0]
                lontext = locations[1]
                #纯数字            
                lattext=lattext.strip('|')                    
                lontext=lontext.strip('|')                    
                #分割数字        
                lat=re.split('\|',lattext)
                lon=re.split('\|',lontext)
                
                latnum=float(lat[0])
                if len(lat)==2:
                    latnum=latnum+float(lat[1])/60.0
                if len(lat)==3:
                    latnum=latnum+float(lat[1])/60.0 + float(lat[2])/3600.0
                    
                lonnum=float(lon[0])
                if len(lon)==2:
                    lonnum=lonnum+float(lon[1])/60.0
                if len(lon)==3:
                    lonnum=lonnum+float(lon[1])/60.0 + float(lon[2])/3600.0
            tabledata["lat"] = latnum
            tabledata["lon"] = lonnum             
            data["Coord"] = tabledata        
   
    #解析schemal文件对应的信息框，其他的忽略
    def parse_infobox_based_shemal(self,content,data):    
        #box_occurences = re.split('{{infobox[^\n}]*\n', content.lower())
        box_occurences = re.split('{{infobox[^\n}]*[\n\"]', content.lower())
        
        if len(box_occurences) < 2:
            return None

        boxes = re.findall('infobox[^\n}]*[\n\"]', content.lower())
        for boxname in boxes:         
            boxname = boxname.strip() 
            if boxname not in self.infoboxschemal.keys():
                print boxname+'\n'
                schemaldata = self.get_infobox_schemal(boxname)
                if schemaldata:
                    if len(schemaldata)>0:
                        self.infoboxschemal[boxname] = schemaldata                
                else:
                    continue;
                
        index =0        
        for box_occurence in box_occurences[1:]:
            boxname = boxes[index].strip()
            if boxname in self.infoboxschemal.keys():   
                infobox_end = re.search('\n[^\n{]*\}\}[^\n{]*\n', box_occurence)    
                if infobox_end is None:
                    return None
        
                box_occurence = box_occurence[:infobox_end.start():]
                box_occurence = re.split('\n[^|\n]*\|', box_occurence)
                
                tabledata = {}
                if self.currentpageid != 0:
                    tabledata['id'] = self.currentpageid
                    tabledata['article_name'] = self.currentarticlename
                boxname = boxes[index]
                boxname = boxname.strip()
                
                for item in box_occurence:
                    item = self.parse_tags(item)
                    item = self.clean_data(item)
                    if '=' in item:
                        pair = item.split('=', 1)
                        field = pair[0].strip()
                        field = re.sub('\|', '', field)
                        #检查是否包含中文，待完善
                        m = re.match(u'[\u4E00-\u9FA5]+', field)
                        if m is None:
                            if boxname in self.infoboxschemal.keys():                    
                                schemal = self.infoboxschemal[boxname]
                                if schemal:
                                    if field in schemal.keys() and len(schemal[field])>1: 
                                        field = schemal[field]
                                               
                        value = pair[1].strip()
                        if value != '' and self.valid(field):
                            tabledata[field.lower()] = value
                            
                data[boxname] = tabledata
                index=index+1
                
        return data
    
    #解析所有的信息框，不管有没有对应的shemal信息
    def parse_infobox(self,content,data):    
        #box_occurences = re.split('{{infobox[^\n\|}]*\n', content.lower())
        box_occurences = re.split('{{infobox[^\n}]*[\n\"]', content.lower())
        
        if len(box_occurences) < 2:
            return None
        # 查找
        boxes = re.findall('infobox[^\|\n}]*[\n\"]', content.lower())    
         
        if(len(boxes)==0):
            return None;   
                         
        index =0        
        for box_occurence in box_occurences[1:]:
            try:
                boxname = boxes[index].strip()
                #验证名称是否有效
                if not self.validbox(boxname):
                    continue
                
                infobox_end = re.search('\n[^\n{]*\}\}[^\n{]*\n', box_occurence)    
                if infobox_end is None:
                    return None
        
                box_occurence = box_occurence[:infobox_end.start():]
                box_occurence = re.split('\n[^|\n]*\|', box_occurence)
                
                tabledata = {}
                if self.currentpageid != 0:
                    tabledata['id'] = self.currentpageid
                    tabledata['article_name'] = self.currentarticlename

                #处理的对象
                print boxname+'\n'
                for item in box_occurence:
                    item = self.parse_tags(item)
                    item = self.clean_data(item)
                    if '=' in item:
                        pair = item.split('=', 1)
                        field = pair[0].strip()
                        field = re.sub('\|', '', field)
                        value = pair[1].strip()
                        if value != '' and self.validfield(field):
                            tabledata[field.lower()] = value
            except Exception,e:
                continue;
            #记录内容                          
            data[boxname] = tabledata
            index=index+1
                
        return data
    #解析所有的模板框
    def parse_template(self,content,data):    
        #box_occurences = re.split('{{infobox[^\n\|}]*\n', content.lower())
        box_occurences = re.split('{{[^\n}]*[\n\"]', content.lower())
        
        if len(box_occurences) < 2:
            return None
        # 查找
        boxes = re.findall('{{[^\|\n}]*[\n\"]', content.lower())
         
        if(len(boxes)==0):
            return None;   
                         
        index =0        
        for box_occurence in box_occurences[1:]:
            try:
                boxname = boxes[index].strip()
                boxname = boxname.strip('{{')        
                #验证名称是否有效
                if not self.validbox(boxname):
                    continue
                
                infobox_end = re.search('\n[^\n{]*\}\}[^\n{]*\n', box_occurence)    
                if infobox_end is None:
                    return None
        
                box_occurence = box_occurence[:infobox_end.start():]
                box_occurence = re.split('\n[^|\n]*\|', box_occurence)
                
                tabledata = {}
                if self.currentpageid != 0:
                    tabledata['id'] = self.currentpageid
                    tabledata['article_name'] = self.currentarticlename

                #处理的对象
                print boxname+'\n'
                for item in box_occurence:
                    item = self.parse_tags(item)
                    item = self.clean_data(item)
                    if '=' in item:
                        pair = item.split('=', 1)
                        field = pair[0].strip()
                        field = re.sub('\|', '', field)
                        value = pair[1].strip()
                        if value != '' and self.validfield(field):
                            tabledata[field.lower()] = value
            except Exception,e:
                       continue;
            #记录内容                          
            data[boxname] = tabledata
            index=index+1
                
        return data    
    #验证字符串是否有效
    def validfield(self,field):
        fieldstring = field.decode('utf8')
        if len(fieldstring) > 50:
            return False
        if u'截至'.decode('utf8') in fieldstring:
            return False
        if u'截止'.decode('utf8') in fieldstring:
            return False
        #if re.match(u'[截至\|截止]',field):
        #   return False
    
        return True
    
    #验证信息框是否有效
    def validbox(self,box):
        if u':'.decode('utf8') in box:
            return False
        #2015-10-18 15:02:38，如果包含citation、noteta、cite、quote、navboxes等信息，也无效
        if u'cit'.decode('utf8') in box:
            return False
        #2015-10-18 15:02:38，如果包含citation、noteta、cite、quote，也无效
        if u'noteta'.decode('utf8') in box:
            return False
        #2015-10-18 15:02:38，如果包含citation、noteta、cite、quote，也无效
        if u'quote'.decode('utf8') in box:
            return False
        #2015-10-18 15:02:38，如果包含citation、noteta、cite、quote，也无效
        if u'navboxes'.decode('utf8') in box:
            return False
        #2015-10-18 15:02:38，如果包含citation、noteta、cite、quote，也无效
        if u'Gallery'.decode('utf8') in box:
            return False
        return True;
    
    def get_infobox_schemal(self,infoboxname):
        filename = infoboxname.replace(" ","_")
        #读取schemal文件，解析其对应的中文名称
        pwd = os.getcwd()
        filename = os.path.join(pwd,filename)
        
        if os.path.isfile(filename):        
            schemalfile = open(filename,'r')        
            content = schemalfile.read()
            schemalfile.close()
            regexstring = '{{'+ infoboxname+'\n'
            data = {}
            box_occurences = re.split(regexstring, content.lower())
            boxes = re.findall('{{[a-z]+box[^\n}]*\n', content.lower())
            if len(box_occurences) < 2:
                return data
            
            for box_occurence in box_occurences[1:]:
        
                infobox_end = re.search('\n[^\n{]*\}\}[^\n{]*\n', box_occurence)
        
                if infobox_end is None:
                    return None
        
                box_occurence = box_occurence[:infobox_end.start():]
                box_occurence = re.split('\n[^|\n]*\|', box_occurence)
        
                for item in box_occurence:
                    item = self.parse_tags(item)
                    item = self.clean_data_with_text(item)
                    if '=' in item:
                        pair = item.split('=', 1)
                        field = pair[0].strip()
                        field = re.sub('\|', '', field)
                        value = pair[1].strip()
                        if value != '' and self.valid(field):
                            data[field.lower()] = value
        
            return data
        else:
            return None;
            
