#-*- coding: utf-8 -*-
from myparser import MyParser

'''
0 : PGM_ID
1 : BRWS_TRANS_ID
2 : BRWS_TRANS_NM
3 : NST_NUM
4 : BRWS_PRT_DLOAD_CL_CD
5 : ONLINE_BAT_CL_CD
6 : LOG_OP_CL_CD
7 : USE_YN
8 : AUDIT_ID
9 : AUDIT_DTM
10 : LOG_NAPLY_RSN_CTT
'''
class ZNGM_SCRN_BRWS_TRANS_Row():
    pgm_id, brws_trans_id, brws_prt_dload_cl_cd, online_bat_cl_cd, log_op_cl_cd, use_yn = '', '', '', '', '', ''
    
    def __init__(self, trans_list):
        self.clear()
        
        self.pgm_id               = trans_list[0]
        self.brws_trans_id        = trans_list[1]
        self.brws_prt_dload_cl_cd = trans_list[4]
        self.online_bat_cl_cd     = trans_list[5]
        self.log_op_cl_cd         = trans_list[6]
        self.use_yn               = trans_list[7]
        
    def clear(self):
        self.pgm_id, self.brws_trans_id, self.brws_prt_dload_cl_cd, self.online_bat_cl_cd, self.log_op_cl_cd, self.use_yn = '', '', '', '', '', ''

    def get(self):
        return "%13s | %18s | %20s | %16s | %12s | %6s" % (self.pgm_id, self.brws_trans_id, self.brws_prt_dload_cl_cd, self.online_bat_cl_cd, self.log_op_cl_cd, self.use_yn)
        
    def show(self):
        print(self.get())
        
    def write(self, wfile):
        wfile.write(self.get() + '\n')
                
class ZNGM_SCRN_BRWS_TRANS:
    parser = MyParser()
    scrnBrwsRows = []
    
    def __init__(self, filename):
        self.clear()
        
        f = open(filename, 'r')
        
        _trans_lines = []
        _trans_lines = f.readlines()
        
        for line in _trans_lines:
            self.parser.clear()

            # remove tag
            self.parser.feed(line.replace("%^^", ""))
            
            # append into list
            self.scrnBrwsRows.append(ZNGM_SCRN_BRWS_TRANS_Row(self.parser.getList()))
        
    def clear(self):
        self.parser.clear()
        self.scrnBrwsRows = []
        
    def header(self):
        header = "%13s | %18s | %20s | %16s | %12s | %6s" % ('PGM_ID', 'BRWS_TRANS_ID', 'BRWS_PRT_DLOAD_CL_CD', 'ONLINE_BAT_CL_CD', 'LOG_OP_CL_CD', 'USE_YN')
        
        return "-" * len(header) + '\n' + header + '\n' + "-" * len(header)

    def show(self):
        print(self.header())
        
        for row in self.scrnBrwsRows:
            row.show()
            
    def write(self, wfile):
        wfile.write(self.header() + '\n')
        
        for row in self.scrnBrwsRows:
            row.write(wfile)