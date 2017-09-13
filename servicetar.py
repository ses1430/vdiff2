#-*- coding: utf-8 -*-
import os
import tarfile
import mycommon

from zngm_scrn_brws_trans import ZNGM_SCRN_BRWS_TRANS
from io_transaction_detail import IO_TRANSACTION_DETAIL
from iofrmt_mst import IOFRMT_MST

class ServiceTar:
    # common
    file = ''       # C:\HarModule\temp\6347588709989367092.tmp
    path = ''       # C:\HarModule\temp\6347588709989367092\
    name = ''       # ordsb0200010t02    
    newFile = ''    # C:\HarModule\temp\6347588709989367092.tmp.diff
    
    # filenames
    pgiFile = ''
    scrnBrwsTransFile = ''
    ioTransDtlFile = ''
    iofrmtMstFileList = []  # IOFRMT_MST filename list
    
    # content of files (string, class)
    pgiContents = ''        
    scrnBrwsTrans = ''      # ZNGM_SCRN_BRWS_TRANS class
    ioTransDtl = ''         # IO_TRANSACTION_DETAIL class
    iofrmtMst  = ''         # IOFRMT_MST class
    
    def __init__(self, p_file, p_path, p_name):
        self.clear()
        
        self.file, self.path, self.name = p_file, p_path, p_name
        
        self.newFile = self.file + '.diff'  # modified & generated filename for diff
        
        self.untar()
        self.analyze()
        self.write()
        
    def getNewFile(self):
        return self.newFile
        
    def clear(self):        
        # common
        self.file = ''       # C:\HarModule\temp\6347588709989367092.tmp
        self.path = ''       # C:\HarModule\temp\6347588709989367092\
        self.name = ''       # ordsb0200010t02    
        self.newFile = ''    # C:\HarModule\temp\6347588709989367092.tmp.diff
        
        # filenames
        self.pgiFile = ''
        self.scrnBrwsTransFile = ''
        self.ioTransDtlFile = ''
        self.iofrmtMstFileList = []  # IOFRMT_MST filename list
        
        # content of files (string, class)
        self.pgiContents = ''        
        self.scrnBrwsTrans = ''      # ZNGM_SCRN_BRWS_TRANS class
        self.ioTransDtl = ''         # IO_TRANSACTION_DETAIL class
        self.iofrmtMst = ''          # IOFRMT_MST class
        
        
    # 파일을 압축해제한다. 
    def untar(self):
        try:
            os.makedirs(self.path)
        except OSError as e:
            print(e)
            
        tar = tarfile.open(self.file)
        
        members = tar.getmembers()
        postfix = 0
        
        # service tar 첫번째 압축해제
        for member in members:
            memname = member.name
            
            # ######################################################################
            # 압축해제 대상
            # 
            # 1. LOADER_C : ZNGM_SCRN_BRWS_TRANS
            # 2. LOADER_U : IO_TRANSACTION_DETAIL
            # 3. LOADER_I : IOFRMT_MST
            # 4. pgi
            # ######################################################################
            if memname[0:8] in ['LOADER_C', 'LOADER_U', 'LOADER_I'] or memname.endswith('.pgi'):
                tar.extract(member, self.path)
                print('%s untar complete.' % memname)
                
                if memname.endswith('tar.gz'):
                    mode = 'r:gz'
                else:
                    mode = 'r'
                
                # 1. LOADER_C : ZNGM_SCRN_BRWS_TRANS
                if memname.startswith('LOADER_C'):
                    in_tar = tarfile.open(self.path + memname, mode)
                    
                    in_members = in_tar.getmembers()
                    
                    for in_member in in_members:                
                        if in_member.name == 'ZNGM_SCRN_BRWS_TRANS.dat':
                            in_tar.extract(in_member, self.path)
                            self.scrnBrwsTransFile = self.path + in_member.name
                        
                    in_tar.close()
                
                # 2. LOADER_U : IO_TRANSACTION_DETAIL                
                elif memname.startswith('LOADER_U'):
                    in_tar = tarfile.open(self.path + memname, mode)
                    
                    in_members = in_tar.getmembers()
                    
                    for in_member in in_members:                
                        if in_member.name == 'IO_TRANSACTION_DETAIL.dat':
                            in_tar.extract(in_member, self.path)
                            self.ioTransDtlFile = self.path + in_member.name
                        
                    in_tar.close()
                
                # 3. LOADER_I : IOFRMT_MST
                elif memname.startswith('LOADER_I'):
                    in_tar = tarfile.open(self.path + memname, mode)
                    
                    in_members = in_tar.getmembers()
                    
                    for in_member in in_members:                
                        if in_member.name == 'IOFRMT_MST.dat':
                            in_tar.extract(in_member, self.path)
                    
                    # IOFRMT_MST 파일은 여러개가 있기 때문에 script 이름을 뒤에 붙여서 unique한 파일명으로 바꾼다.
                    try:    
                        os.rename(self.path + 'IOFRMT_MST.dat', self.path + 'IOFRMT_MST' + str(postfix) + '.dat')
                    except:
                        pass
                        
                    self.iofrmtMstFileList.append(self.path + 'IOFRMT_MST' + str(postfix) + '.dat')
                    postfix = postfix + 1
                    
                    in_tar.close()
                
                # 4. pgi
                elif memname.endswith('pgi'):
                    self.pgiFile = self.path + memname  # C:\HarModule\temp\6347588709989367092\ordsb0200010t01.pgi
                    
        tar.close()
    
    # 파일을 분석한다.
    def analyze(self):
        # 1. pgi
        try:
            rfile = open(self.pgiFile, 'r')
            
            self.pgiContents = rfile.readline()
        except OSError as e:
            print(e)
        finally:
            rfile.close()
    
        # 2. ZNGM_SCRN_BRWS_TRANS.dat
        if len(self.scrnBrwsTransFile):
            self.scrnBrwsTrans = ZNGM_SCRN_BRWS_TRANS(self.scrnBrwsTransFile)   
            
        # 3. IO_TRANSACTION_DETAIL.dat
        if len(self.ioTransDtlFile):
            self.ioTransDtl    = IO_TRANSACTION_DETAIL(self.ioTransDtlFile)    
        
        # 4. IOFRMT_MST files (multi)
        if len(self.iofrmtMstFileList):
            self.iofrmtMst = IOFRMT_MST(self.iofrmtMstFileList)
            
    
    # stout 에 출력한다.
    def show(self):
        # 1. pgi
        print(mycommon.get_div_header("1. PGI INFO"))
        print(self.pgiContents)
        
        # 2. ZNGM_SCRN_BRWS_TRANS.dat
        if len(self.scrnBrwsTransFile):
            print(mycommon.get_div_header("2. ZNGM_SCRN_BRWS_TRANS INFO"))
            self.scrnBrwsTrans.show()
            
        # 3. IO_TRANSACTION_DETAIL.dat
        if len(self.ioTransDtlFile):
            print(mycommon.get_div_header("3. IO_TRANSACTION_DETAIL"))
            self.ioTransDtl.show()
        
        # 4. IOFRMT_MST files (multi)
        if len(self.iofrmtMstFileList):
            print(mycommon.get_div_header("4. IOFRMT_MST"))
            self.iofrmtMst.show()
        
    # diff 파일을 생성한다.
    def write(self):
        wfile = open(self.newFile  , 'w')
     
        # 1. pgi
        wfile.write(mycommon.get_div_header("1. PGI INFO"))
        wfile.write(self.pgiContents)
        wfile.write("\n\n")
        
        # 2. ZNGM_SCRN_BRWS_TRANS.dat
        # 위 파일이 없는 경우도 있음        
        if len(self.scrnBrwsTransFile):
            wfile.write(mycommon.get_div_header("2. ZNGM_SCRN_BRWS_TRANS INFO"))
            self.scrnBrwsTrans.write(wfile)
        
        # 3. IO_TRANSACTION_DETAIL.dat
        if len(self.ioTransDtlFile):
            wfile.write(mycommon.get_div_header("3. IO_TRANSACTION_DETAIL"))
            self.ioTransDtl.write(wfile)
        
        # 4. IOFRMT_MST files (multi)
        if len(self.iofrmtMstFileList):
            wfile.write(mycommon.get_div_header("4. IOFRMT_MST"))
            self.iofrmtMst.write(wfile)
        
        wfile.close()
