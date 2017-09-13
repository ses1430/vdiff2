# -*- coding: utf-8 -*-
from myparser import MyParser

# IO_TRANSACTION_DETAIL 파일에 해당하는 class
class IO_TRANSACTION_DETAIL_Row():
    trxcode, iogbn, svcname, fieldname, fielddesc, fieldtype = '', '', '', '', '', ''
    recindex, colindex, fieldlenth = 0, 0, 0
    
    def __init__(self, p_list):
        self.clear()        
        self.trxcode    = p_list[0]
        self.iogbn      = p_list[1].split('|')[1] 
        self.recindex   = int(p_list[2])
        self.colindex   = int(p_list[3])
        self.svcname    = p_list[4]
        self.fieldname  = p_list[5]
        self.fielddesc  = p_list[6]
        self.fieldtype  = p_list[7]
        self.fieldlenth = int(p_list[8])
        
    def clear(self):
        self.trxcode, self.iogbn, self.svcname, self.fieldname, self.fielddesc, self.fieldtype = '', '', '', '', '', ''
        self.recindex, self.colindex, self.fieldlenth = 0, 0, 0

    def get(self):
        # return "%2s | %3s | %3s | %50s | %10s | %11s" % (self.iogbn, self.recindex, self.colindex, self.fieldname, self.fieldtype, self.fieldlenth)
        return "%2s | %3s | %50s | %3s | %10s | %11s" % (self.iogbn, self.recindex, self.fieldname, self.colindex, self.fieldtype, self.fieldlenth)
        
    def show(self):
        print(self.get())
        
    def write(self, wfile):
        wfile.write(self.get() + '\n')
                
class IO_TRANSACTION_DETAIL:
    parser = MyParser()
    iotransRows = []
    
    def __init__(self, p_filename):
        self.clear()
        
        f = open(p_filename, 'r')
        
        _iotrans_lines = []
        _iotrans_lines = f.readlines()
        
        for line in _iotrans_lines:
            self.parser.clear()
            
            # remove tag
            self.parser.feed(line.replace("%^^", ""))
            
            # append into list
            self.iotransRows.append(IO_TRANSACTION_DETAIL_Row(self.parser.getList()))
        
        # recindex, colindex가 숫자형태로 정렬이 안되어 있어 정렬필요
        self.iotransRows = sorted(self.iotransRows, key = lambda x : (x.iogbn, x.recindex, x.colindex))
        
    def clear(self):
        self.iotransRows = []
        
    def header(self):
        # header = "%2s | %3s | %3s | %50s | %10s | %11s" % ('G', 'RID', 'CID', 'FIELDNAME', 'FIELDTYPE', 'FIELDLENGTH')
        header = "%2s | %3s | %50s | %3s | %10s | %11s" % ('G', 'RID', 'FIELDNAME', 'CID', 'FIELDTYPE', 'FIELDLENGTH')
        
        return "-" * len(header) + '\n' + header + '\n' + "-" * len(header) + "\n"

    def show(self):
        print(self.header())
        
        for row in self.iotransRows:
            row.show()
            
    def write(self, wfile):
        wfile.write(self.header())
        
        for row in self.iotransRows:
            row.write(wfile)