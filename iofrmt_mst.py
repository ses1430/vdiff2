#-*- coding: utf-8 -*-
from myparser import MyParser

# struct, message 내의 항목 1개 SET를 관리
# 아래와 같이 declare(include) + property (N개) + comment 가 하나의 set임
# ex) 	INCLUDE(ins_01, "/a0_ordssub90110t01_ins_01_msg");
#    	PROPERTY(ins_01, ARRAY0, rec_cnt_1);
#   	COMMENT("고객기준조회조건");
class Record:
    type, name, include, length, array0, comment, masq = '', '', '', '', '', '', ''
    
    def __init__(self, p_type, p_name, p_include, p_length, p_array0, p_comment, p_masq):
        self.clear()
        
        self.type = p_type.strip()
        self.name = p_name.strip()
        self.include = p_include.strip()
        self.length = p_length.strip()
        self.array0 = p_array0.strip()
        self.comment = p_comment.strip()
        
        if p_masq.strip():
            self.masq = p_masq.strip().upper()
        else:
            self.masq = 'FALSE'
        
    def clear(self):
        self.type, self.name, self.include, self.length, self.array0, self.comment, self.masq = '', '', '', '', '', '', ''
    
    def get(self):
        return "%8s | %-45s | %-33s | %5s | %-15s | %5s" % (self.type, self.name, self.include, self.length, self.array0, self.masq)
        
    def show(self):
        print(self.get())
        
    def write(self, wfile):
        wfile.write(self.get() + '\n')

# struct, message 단위와 매핑되는 클래스
# category, name, owner, script_type, script로 구성됨
# script는 항목별로 추가 parsing하여 Script 구조체 배열로 관리
class Script:
    category, name, user_name, script_type, script = '', '', '', '', ''    
    recordArray = []   # Record class array
    
    def __init__(self, p_list):
        self.clear()
        
        self.category, self.name, self.user_name, self.script_type = p_list[0], p_list[1], p_list[2], p_list[3]
        
        # merge "script01 ~ script20"
        for i in range(4,23):
            if not p_list[i]: 
                break
            self.script = self.script + p_list[i]
        
        self.analyze()
    
    def __lt__(self, other):
        if self.script_type != other.script_type:
            return self.script_type < other.script_type
        else:
            return self.name < other.name
    
    def clear(self):
        self.category, self.name, self.user_name, self.script_type, self.script = '', '', '', '', ''
        self.recordArray = []
        
    def show(self):
        print(self.header())
        
        for record in self.recordArray:
            record.show()
            
    def write(self, wfile):
        wfile.write(self.header() + '\n')
        
        for record in self.recordArray:
            record.write(wfile)
        
    def header(self):
        #header1 = " # name [%s] user_name [%s] script_type [%s]" % (self.name, self.user_name, self.script_type)
        header1 = " # name [%s] script_type [%s]" % (self.name, self.script_type)
        header2 = "%8s | %-45s | %-33s | %5s | %-15s | %-5s" % ("type", "name", "include", "len", "array0", "masq")
        
        return "-" * len(header2) + "\n" + header1 + "\n" + "-" * len(header2) + '\n' + header2 + '\n' + "-" * len(header2)
    
    # generate script_formatted class array with "script" variable
    def analyze(self):
        if not len(self.script):
            print("script is null")
            return False
        
        # formatting is for "message", "struct"
        if self.script_type == 'M' or self.script_type == 'S':
            typ, name, include, length, array0, comment, masq = '', '', '', '', '', '', ''
            
            # tokenize : {a,b,c} -> a b c
            script_list = self.script.split("{")[1].split("}")[0].split("\n\t")
            
            for e in script_list:
                # 다음 declare나 include를 만나면 insert
                if (e.startswith("DECLARE") or e.startswith("INCLUDE")) and len(typ):
                    self.recordArray.append(Record(typ, name, include, length, array0, comment, masq))
                    
                    typ, name, include, length, array0, comment, masq = '', '', '', '', '', '', ''
                
                # DECLARE(INTEGER, rec_cnt_1, LENGTH, 5);
                if e.startswith("DECLARE"):
                    in_list = e.split('(')[1].split(')')[0].split(',')
                    
                    typ, name, length = in_list[0], in_list[1], in_list[3]
                    
                    #print "-> DECLARE : ", type, name, length
                
                # INCLUDE(ins_01, "/b0_ordssub90110t01_ins_01_msg");
                elif e.startswith("INCLUDE"):                
                    in_list = e.split('(')[1].split(')')[0].split(',')
                    
                    typ = "INCLUDE"
                    name = in_list[0]
                    include = in_list[1].replace('"', '')
                    
                    #print "-> INCLUDE : ", type, name, include
                    
                # PROPERTY(ins_01, ARRAY0, rec_cnt_1);
                # PROPERTY(ins_01, MASQUERADE, FALSE);
                elif e.startswith("PROPERTY"):
                    in_list = e.split('(')[1].split(')')[0].split(',')
                    
                    if in_list[1].strip() == 'ARRAY0':
                        array0 = in_list[2]
                    elif in_list[1].strip() == 'MASQUERADE':
                        masq = in_list[2]
                    #print "-> PROPERTY : ", array0, masq
                        
                # COMMENT("고객기준조회조건");
                elif e.startswith("COMMENT"):
                    in_list = e.split('(')[1].split(')')[0].split(',')
                    
                    comment = in_list[0].replace('"', '')
            
            # 마지막으로 한번 append
            self.recordArray.append(Record(typ, name, include, length, array0, comment, masq))            
                    
class IOFRMT_MST:    
    scriptArray = []
    
    def __init__(self, file_list):
        self.clear()

        for filename in file_list:
            f = open(filename, "r")
            print(filename, "open...")
            
            # IOFRMT_MST 파일안에 여러개의 script가 delimeter("%^^")로 구분되어 여러개가 들어있음
            text = f.read()
            
            if text.startswith("%^^"):
                tokens = text.split("%^^")
            elif text.startswith("^"):
                tokens = text.split("^")
            
            parser = MyParser()
            
            for token in tokens:
                if len(token) > 0:
                    parser.clear()
                    parser.feed(token)
                    
                    vlist = []
                    vlist = parser.getList()
                    
                    # message나 struct만 parsing한다. ASSIGN 만 들어있는 s2m, m2s는 팝콘이나 가져와라.
                    if vlist[3] == 'M' or vlist[3] == 'S':                    
                        self.scriptArray.append(Script(vlist))
            
            f.close()
        
        self.scriptArray.sort()
        
    def clear(self):
        self.scriptArray = []
    
    def header(self):
        pass

    def show(self):
        # print self.header()
        
        for script in self.scriptArray:
            script.show()
            
    def write(self, wfile):
        # wfile.write(self.header() + '\n\n')
        
        for script in self.scriptArray:
            script.write(wfile)
    