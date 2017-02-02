#-*- coding: UTF-8 -*-
import scraperwiki
import xlwt
import csv
import codecs
from _codecs import decode
import json

class filewriter():

    def  SaveToSQLite(self,data_dict):   
        try:                   
            for tablename in data_dict.keys():
                data_list = data_dict[tablename]                
                tablename = tablename.replace(" ","_")
                if len(data_list) > 0:
                    scraperwiki.sql.save(['id'], data_list,table_name=tablename)
        except Exception,e:
            raise Exception(e)
        
    # 将字典中的数据存储为Excel 
    def SaveToExcel(self,data_dict):    
        #data结构：{tablename,[{columnname,value}]}  
        wbk = xlwt.Workbook()      
        try:                   
            for tablename in data_dict.keys():
                data_list = data_dict[tablename]                
                tablename = tablename.replace(" ","_") 
                tablename = tablename.decode('utf8')                
                sheet = wbk.add_sheet(tablename) #插入Excel标签页

                #寻找key最多的datatable，作为默认的列，后面有新的，再增加新列。
                maxtable=data_list[0];
                for datatable in data_list:
                    if ( len(maxtable.keys())>len(datatable.keys()) ):
                        maxtable = datatable;
            
                #列索引
                columnindex = 1;
                #列名称字典，功后面使用
                columndict = {}
                #输入名称
                sheet.write(0, 0, '名称'.decode('utf-8'))
                columndict['article_name']= 0;
                for columnkey in maxtable.keys() :
                    if columnkey == u'article_name':
                        continue;
                    
                    sheet.write(0, columnindex, columnkey)
                    columndict[columnkey]= columnindex;
                    columnindex+=1                    
                
               #逐行插入
                rowindex = 1
                for datatable in data_list:                  
                    for key in datatable.keys():
                        #如果列名称字典中没有，在后面插入新列
                        if(key not in columndict.keys()):
                            columnindex = len(columndict.keys())
                            columndict[key]= columnindex;
                            sheet.write(0, columnindex, key.decode('utf8'))
                            
                        value = datatable[key]
                        if isinstance(value,unicode):
                            value = value.decode('utf-8')
                        else :
                            if isinstance(value,basestring):
                                #待完善，value先转换为unicode,然后在转换为utf8编码的string
                                value = value.decode('utf-8').encode('utf-8')

                        columnindex =  columndict[key]
                        sheet.write(rowindex,columnindex, value)
                    
                    rowindex+=1
                
            #存储，注意filename需要为utf8的str对象                    
            wbk.save(u'抽取结果.xls'.decode('utf8')) 
                
        except Exception,e:
            wbk.save('Unfinised.xls' ) 
            raise Exception(e)
        
    def SaveToCSV(self,data_dict):   
        try:                   
            for tablename in data_dict.keys():
                data_list = data_dict[tablename]                
                tablename = tablename.replace(" ","_")
                filename = tablename+'.csv'
                filename = filename.decode('utf8')
                csvfile = open(filename, 'wb')
                #重要！实现中文编码
                csvfile.write(codecs.BOM_UTF8)
                spamwriter = csv.writer(csvfile,dialect='excel')
                datatable = data_list[0]
                spamwriter.writerow([datatable.keys()[0].encode('utf8'), datatable.keys()[1].encode('utf8'), datatable.keys()[2].encode('utf8'), datatable.keys()[3].encode('utf8'), datatable.keys()[4].encode('utf8')])
                               
                #判断是否为unicode对象
                for datatable in data_list:
                    data0 = datatable[datatable.keys()[0]]
                    data1 = datatable[datatable.keys()[1]]
                    data2 = datatable[datatable.keys()[2]]
                    data3 = datatable[datatable.keys()[3]]
                    data4 = datatable[datatable.keys()[4]]
                    
                    if isinstance(data0, unicode):
                        data0=data0.encode('utf8')
                    if isinstance(data1, unicode):
                        data1=data1.encode('utf8')  
                    if isinstance(data2, unicode):
                        data2=data2.encode('utf8')
                    if isinstance(data3, unicode):
                        data3=data3.encode('utf8')
                    if isinstance(data4, unicode):
                        data4=data4.encode('utf8')                  
                    spamwriter.writerow([data0,data1,data2,data3,data4])               
                
                csvfile.close()
        except Exception,e:
            raise Exception(e)
        
    def SaveToJSON(self,data_dict,pageid): 
        #data结构：{tablename,[{columnname,value}]} 
        try:                   
            filename=pageid+".json"
            file = codecs.open(filename, 'wb', encoding='utf-8')
            line = json.dumps(data_dict,indent=1) + '\n'
            file.write(line.decode("unicode_escape"))
            file.close()
                
        except Exception,e:
            raise Exception(e)