#-*- coding: UTF-8 -*-
#!/usr/bin/env python

import sys
import os
import re
import requests
import codecs
import configuration

# Allow unicode characters to be printed.
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
#api_url = 'http://zh.wikipedia.org/w/api.php?action=query&format=json'

class wikiextractor():
    def __init__(self):
        self.infoboxschemal = {}
        #self.clear_db()
        self.currentpageid=0
        self.currentarticlename=""
        
   # def clear_db(self):
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
        data = re.sub('(?i)\{\{cite .*\}\}', '', data)
        data = re.sub('&nbsp;', '', data)
        return data
    
    def clean_data_with_text(self,data):
        # Strip square brackets.
        data = re.sub('\[\[.*\]\]', '', data)
        # Strip all HTML tags.
        data = data.replace('<!--', '' )
        data = data.replace('-->', '' )
        #data = re.sub(u'閿熸枻鎷�.*閿熸枻鎷�', '',data)
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
                        
         #閿熸枻鎷烽敓鏂ゆ嫹閿熸帴缁撴瀯
        for subcategory in subcategories:
            subcategory = subcategory.replace('Category:', '')
            self.parse_members(subcategory, data_dict, include_subcat )
                

    def getjson(self,url):
        try:
            request = requests.get(url)
            json_content = request.json()
            return json_content
        except Exception,e:
            raise Exception(u'网络连接失败，请检查')     
            
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
           
            self.parse_province(content,data)
            self.parse_coord(content,data)
            self.parse_infobox(content,data)
            
            return data
        except Exception,e:
            raise e
            
  
    #解析坐标信息
    #TODO,有bug，待完善
    def parse_coord(self,content,data):
        
        tabledata = {}
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
    
    #解析中国省份模板
    def parse_province(self,content,data):    
        #province_occurences= re.findall(u'{{中国省份(.*\n)*}}', content)        
        province_occurences = re.split(u'{{中国省份', content)
        if len(province_occurences)<2:
            return
        
        tabledata = {}
        tabledata['id'] = self.currentpageid
        tabledata['article_name'] = self.currentarticlename
        for province_occurence in province_occurences[1:]:
    
            infobox_end = re.search(u'\n[^\n{]*\}\}[^\n{]*\n', province_occurence, re.U)
    
            if infobox_end is None:
                return
    
            province_occurence = province_occurence[:infobox_end.start():]
            province_occurence = re.split(u'\n[^|\n]*\|', province_occurence)
    
            for item in province_occurence:
                item = self.parse_tags(item)
                item = self.clean_data(item)
                if '=' in item:
                    pair = item.split('=', 1)
                    field = pair[0].strip()
                    field = re.sub('\|', '', field)
                    value = pair[1].strip()
                    if value != '':
                        tabledata[field] = value
    
        data[u'中国省份'] = tabledata
    
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
        for boxname in boxes:           
            boxname = boxname.strip()            
         
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
        return TabError;
    
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
            
