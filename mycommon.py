#-*- coding: utf-8 -*-
import tarfile

from datetime import datetime

# common codes
dic_dbio_type = {'P':'Persist', 'V':'View', 'D':'Dynamic' , 'E':'Execute'}

# ****************************************************
# 압축을 해제할 디렉토리 명을 리턴한다 (파일명에서 확장자 삭제)
# 
# input : C:\HarModule\temp\6347588709989367092.tmp
# output : C:\HarModule\temp\6347588709989367092\
#
# ****************************************************
def get_path_for_untar(fullpath):
    return fullpath[0: fullpath.rfind('.')] + '\\'

# ****************************************************
# 압축을 해제할 디렉토리 명을 리턴한다 (파일명에서 확장자 삭제)
# 
# input : P, V, D, E
# output : Persist, View, Dynamic, Execute
# 
# ****************************************************
def get_dbio_map_type(key):
    return dic_dbio_type[key]

# ****************************************************
# 파일에 쓸때 사용하기 위한 div header 문자열 리턴
# ****************************************************
def get_div_header(header):
    return "\n" + "#" * 100 + '\n' + "{0:#^100}".format("{0:^50}".format(header)) + "\n" + "#" * 100 + '\n'

# ****************************************************
# 소스의 유형을 판단한다.
#  ※ 파일명은 랜덤하게 생성되므로, 파일명으로 판단하지 않고 파일 내용 일부를 binary로 읽어들여 prefix로 판단한다.
# 
# 1) LOADER_D : DBIO
# 2) LOADER_I : Service Tar
# 3) z : module tar
#
# input : 파일명 (경로까지 포함된 full-path)
# output : typ (소스 타입 : D (DBIO), S(Service Tar), M(Module tar), P (Plain src))
#          name (소스명 : 서비스면 서비스명, 모듈이면 모듈명, DBIO면 DBIO명...)
#          path (압축해제용 경로)
#
# ****************************************************
def get_source_type(fname):
    f = open(fname, 'rb')
    prefix = f.readline()   # input은 temp파일명으로 들어오므로, 파일명이 아닌 prefix로 소스유형 판단
    
    f.close()
    
    # fname : c:\Harmodule\Temp\sample.tmp
    print(fname)
    
    typ, name = '', ''
    
    # tar 파일인 경우 dbio, service tar, module tar 중 하나임.
    if tarfile.is_tarfile(fname):
        # dbio tar : LOADER_D_zord_svc_s1273_20121010205517.tar.gz
        if prefix.startswith(b'LOADER_D'):
            idx = prefix.find(b'tar.gz')

            name = prefix[9: idx - 16]
            
            typ = 'D'
            # name = str(name, encoding='UTF-8')
            name = str(name)

        # service tar #1 : LOADER_I_ordsb0200010t02_in_20151123113132.tar.gz
        # service tar #2 : LOADER_T_ZNGMSCOD00030_TR01_20080904134349.tar.gz <- 옛날 service Tar는 이렇게 생겼나...
        elif prefix.startswith(b'LOADER'):
            if prefix[9] == 'Z':
                name = prefix[10:27]
                name = str(name)
                name = name.replace("_TR", "T").lower()
            else:
                name = prefix[9:24]
                name = str(name)
            
            typ = 'S'
            
        # module tar
        elif prefix.startswith(b'z'):
            typ = 'M'
            name = prefix[0:13]
    # plain src
    else:
        typ = 'P'
        name = fname[fname.rfind('\\') + 1: fname.rfind('.')]
        
    return typ, name, get_path_for_untar(fname)
    
def timestamp(user_string):
    print('##########', datetime.now(), '########### : ', user_string)