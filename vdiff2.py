#-*- coding: utf-8 -*-
# basic modules
import sys 
import tarfile
import os
import glob
import subprocess
import re

# user-defined modules
import mycommon 
from myparser import MyParser
from servicetar import ServiceTar

# dbio untar       
def untar_dbio_tar(fname, dname):    
    # 디렉토리 미리 생성
    try:
        os.makedirs(dname)
    except OSError as e:
        print(e)
   
    # dbio 첫번째 압축해제
    tar = tarfile.open(fname)
    tar.extractall(dname)
   
    members = tar.getmembers()
    
    # dbio 두번째 압축해제
    for member in members:
        memname = member.name
       
        # dbio는 사실 1차 압축은 파일 하나밖에 없어서 의미없지만 그냥...
        if memname.startswith('LOADER_D'):
            in_tar = tarfile.open(dname + '\\' + memname)
           
            in_members = in_tar.getmembers()   
            
            # 2차 압축해제 - 필요한 파일만 압축해제
            for in_member in in_members:
                if in_member.name in ('DBIO_MAP_SQL.dat', 'DBIO_MAP.dat', 'DBIO_MAP_STRUCT.dat'):
                    in_tar.extract(in_member, dname)
           
            in_tar.close()
   
    tar.close()
    
# module untar
def untarModule(fname):
    dname = fname.replace('.tmp', '')
    
    try:
        os.makedirs(dname)
    except OSError as e:
        print(e)
        
    tar = tarfile.open(fname)
    tar.extractall(dname)
    tar.close()
    
    return dname

# convert dbio text (remove tag)
def formatdbio(path, filename):
    wfname = filename + '.diff'
    wfile = open(wfname  , 'w')
 
    # 1. DBIO_MAP parsing
    rfile = open(path + 'DBIO_MAP.dat', 'r')
    
    map_lines = rfile.read()
    map_lines = map_lines.replace("%^^", "")
    map_lines = map_lines.replace("<endlong>", "</endlong>")
    
    parser = MyParser()
    parser.clear()
    parser.feed(map_lines)
    
    _map_list = []
    _map_list = parser.getList()
    
    wfile.write(mycommon.get_div_header("  1. DBIO_MAP INFO  "))
    
    wfile.write("\nMAP_ID          : %s" % _map_list[0]) 
    wfile.write("\nMAP_TYPE        : %s" % mycommon.get_dbio_map_type(_map_list[2])) 
    wfile.write("\nEXEC_TYPE       : %s" % _map_list[3])
    wfile.write("\nTABLE_NAME      : %s" % _map_list[4])
    wfile.write("\nHINT_STRING     : %s" % _map_list[8])
    wfile.write("\nARRAY_SIZE      : %s" % _map_list[9].split('|')[1])
    wfile.write("\nWORK_USER       : %s" % _map_list[10])
    wfile.write("\nREMARK          : %s" % _map_list[11])
    wfile.write("\nWAIT_TIME       : %s" % _map_list[21])
    
    wfile.write("\n\n[WHERE_STRING]\n%s\n"    % _map_list[5])
    wfile.write("\n\n[GROUP_BY_STRING]\n%s\n" % _map_list[6])
    wfile.write("\n\n[HAVING_STRING]\n%s\n"   % _map_list[7])
    
    rfile.close()
    
    # 2. DBIO_MAP_STRUCT parsing
    rfile = open(path + 'DBIO_MAP_STRUCT.dat', 'r')
    
    wfile.write(mycommon.get_div_header("  2. DBIO_MAP_STRUCT INFO  "))
    
    wfile.write("%2s | %3s | %-55s | %-9s | %-8s | %6s | %-500s\n" % ("G", "IDX", "COL_NAME", "INTYPE", "EXTYPE", "LENGTH", "EXPR"))
    wfile.write("-"*100)
    wfile.write("\n")
    
    while True:
        currline = rfile.readline()
        
        if not currline : break;
       
        # remove tag
        currline = currline.replace("%^^", "")
        currline = currline.replace("<endlong>", "</endlong>")
        
        parser.clear()        
        parser.feed(currline)
        
        _parsed_list = []
        _parsed_list = parser.getList()
        
        text = "%2s | %3s | %-55s | %-9s | %-8s | %6s | %-500s" % (_parsed_list[2], _parsed_list[3].replace("|", ""), _parsed_list[5].strip(), _parsed_list[6], _parsed_list[7], _parsed_list[8].split('|')[1] + ',' + _parsed_list[8].split('|')[2], _parsed_list[9].strip())
        
        wfile.write(text)
        wfile.write("\n")
    
    rfile.close()
    
    wfile.write("\n\n")
    
    # 3. DBIO_MAP_SQL parsing
    rfile = open(path + 'DBIO_MAP_SQL.dat', 'r')
    
    wfile.write(mycommon.get_div_header("  3. DBIO_MAP_SQL INFO  "))
    
    while True:
        currline = rfile.readline()
       
        if not currline : break;
       
        # replace
        # 1 : %^^<startlong>zord_svc_s1273<endlong>|1|1|<startlong>
        # 2 : <endlong>|
        line = currline
        
        # remove tag
        p1 = re.compile('%\^\^<startlong>.*?<endlong>\|[1-9]\|[1-9]*[0-9]\|<startlong>')
        p2 = re.compile('<endlong>\|\n')
        
        line = p1.sub('', line)
        line = p2.sub('', line)
        
        wfile.write(line)

    '''
    lines = ''
    lines = rfile.read()
    
    lines = lines.replace("%^^", "")
    lines = lines.replace("<endlong>", "</endlong>")
    
    parser = MyParser()
    parser.clear()
    parser.feed(lines)
    
    list = []
    list = parser.getList()
    text = ''
    
    # tag 기준으로 잘랐을때 각 token은 4개 부분으로 구성됨
    # 1 : DBIO 명
    # 2 : seq
    # 3 : 실제 쿼리
    # 4 : escape
    #
    # 3번째(idx = 2) 만 붙이면 full sql 이 나옴
    for idx, val in enumerate(list):
        if idx % 4 == 2:
            text = text + val
    
    wfile.write(text)
    '''
    
    rfile.close()
    wfile.close()
    
    return wfname
    
# src diff 실행파일 경로를 설정파일에서 읽어옴
# 원래 vdiff2.exe 실행파일 위치를 찾기 위함.
def get_diff_program_path():
    try:
        f = open("C:\HarModule\external\setting.conf", 'r')       
        # exepath = str(f.readline().strip(), encoding='UTF-8')
        exepath = str(f.readline().strip())
        f.close()
    except:
        exepath = "C:\HarModule\external\vdiff2_old.exe"
        
    print("exepath [%s]" % exepath)
   
    return exepath
    
def excute_view_program(filename):
    #exec_arg = "C:\\Windows\\notepad.exe " + file
    exec_arg = '"C:\\Program Files\\Notepad++\\notepad++.exe" ' + filename
    
    print("exec argument = " + str(exec_arg))
    os.system(exec_arg)
    
# 소스 비교 프로그램을 실행한다
def execute_diff_program(oldfile, newfile):
    cmd = get_diff_program_path()
    
    exec_arg = cmd + ' ' + oldfile + ' ' + newfile
    
    print("exec argument = " + exec_arg)
    # os.system(exec_arg)
    subprocess.call(exec_arg)

# 압축해제한 임시파일 및 디렉토리를 삭제한다.
def remove_temp_dir_files(path):
    # delete all files first
    for f in glob.glob(path + '\\*.*'): 
        os.remove(f)
        
    # delete temp directory when empty
    os.rmdir(path)
    
# main
if __name__ == '__main__':
    mode = ''
    
    if len(sys.argv) < 2:
        print("too few arguments!!")
        sys.exit()
    elif len(sys.argv) == 2 :   # 인자가 하나라면, view 모드
        print("view mode")
        mode = 'view'
    elif len(sys.argv) == 3 :   # 인자가 두개라면, diff 모드
        print("diff mode")
        mode = 'diff'
    else:
        print("too many arguments!!")
        sys.exit()
    
    if sys.argv[0].endswith('vdiff2_old.exe'):
        print("vdiff2_old.exe 파일이 잘못되었습니다.")
        sys.exit()

    # view 모드일 경우 설정파일에 정의된 텍스트편집기로  띄운다
    if mode == 'view':
        filename = sys.argv[1]
        
        (typ, name, path) = mycommon.get_source_type(filename)
        
        if typ == 'D':
            untar_dbio_tar(filename, path)
            diff_file = formatdbio(path)
            excute_view_program(diff_file)
            remove_temp_dir_files(path)
            
        # module tar
        elif typ == 'M' :
            # untar
            untarModule(filename)
            
            # run diff
            excute_view_program(path + name + '.pgi')
        
        # plain source file (.c, .pc, .h ...)
        elif typ == 'P' :
            # run diff
            excute_view_program(filename)
        
        # service I/O tar
        elif typ == 'S' :
            # define class with initialize
            svc_tar = ServiceTar(filename, path, name)
            
            # get full path of modified file for diff
            diff_file = svc_tar.getNewFile()
            
            # run diff
            excute_view_program(diff_file)
            
            remove_temp_dir_files(path)
            
    # diff 모드일 경우 설정파일에 정의된 diff 프로그램을 띄운다
    elif mode == 'diff':
        oldfile = sys.argv[1]
        newfile = sys.argv[2]
        
        print("oldfile [%s]" % oldfile)
        print("newfile [%s]" % newfile)
        print("current path [%s]" % os.getcwd())
        
        (typ_b, name_b, path_b) = mycommon.get_source_type(oldfile)
        (typ_a, name_a, path_a) = mycommon.get_source_type(newfile)
        
        print("bef [%s][%s][%s]" % (typ_b, name_b, path_b))
        print("aft [%s][%s][%s]" % (typ_a, name_a, path_a))
        
        # dbio tar
        if typ_b == 'D' and typ_a == 'D':  
            # untar
            untar_dbio_tar(oldfile, path_b)
            untar_dbio_tar(newfile, path_a)
            
            # remove tag
            diff_file_old = formatdbio(path_b, oldfile)
            diff_file_new = formatdbio(path_a, newfile)
            
            # run diff
            execute_diff_program(diff_file_old, diff_file_new)
            
            # remove temp files (tar.gz)
            remove_temp_dir_files(path_b)
            remove_temp_dir_files(path_a)
            
            '''
            dbio_old = DbioTar(oldfile, path_b, name_b)
            dbio_new = DbioTar(newfile, path_a, name_a)
            
            diff_file_old = dbio_old.getNewFile()
            diff_file_new = dbio_old.getNewFile()
            
            # run diff
            execute_diff_program(diff_file_old, diff_file_new)
            
            remove_temp_dir_files(path_b)
            remove_temp_dir_files(path_a)
            '''
        # module tar
        elif typ_b == 'M' and typ_a == 'M' :
            # untar
            untarModule(oldfile)
            untarModule(newfile)
            
            # run diff
            execute_diff_program(path_b + name_b.decode('utf-8') + '.pgi', path_a + name_a.decode('utf-8') + '.pgi')
        
        # plain source file (.c, .pc, .h ...)
        elif typ_b == 'P' and typ_a == 'P' :
            # run diff
            execute_diff_program(oldfile, newfile)
        
        # service I/O tar
        elif typ_b == 'S' and typ_a == 'S' :
            # define class with initialize
            svc_tar_old = ServiceTar(oldfile, path_b, name_b)
            svc_tar_new = ServiceTar(newfile, path_a, name_a)
            
            # get full path of modified file for diff
            diff_file_old = svc_tar_old.getNewFile()
            diff_file_new = svc_tar_new.getNewFile()
            
            # run diff
            execute_diff_program(diff_file_old, diff_file_new)
            
            remove_temp_dir_files(path_b)
            remove_temp_dir_files(path_a)            
