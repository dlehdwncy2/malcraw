
import sys
import hashlib
import re
import os
from multiprocessing import Process, current_process ,Queue, Pool
import threading
import socket
import datetime
import time
import urllib
import urllib.request
import zipfile
import json
import hashlib
import shutil
from urllib.request import Request, urlopen
import signal
import patoolib
#from unrar import rarfile

import unrar
import rarfile

from requests import get
from pyunpack import Archive
import filetype
from bs4 import BeautifulSoup
import requests

import craw_comm as c_c


def handler(signum,frame):
    raise Exception("timeout")



def unzip_process():
    temp_sample_list=[os.path.join(c_c.PATH_TEMP,fname) for fname in [fname for fname in os.listdir(c_c.PATH_TEMP)]]
    #TEMP 경로에 있는 파일 Unzip 수행
        #Unzip의 경우 zip 내 또 있을 수 있음.
    temp_sample_list=unzip_manager(temp_sample_list)
    
    for temp_sample in temp_sample_list:
        if temp_sample==c_c.PATH_TEMP:continue

        #Unzip 후 하위 디렉토리에 있는 것들 상위로 긁어옴
        dir_move_sample(temp_sample)
        #확장자 별로 파일 이동
            #OTHERS : 알 수 없음
            #ext : 확장자 별 이동
        sample_move_extenstion(temp_sample)
    
    #TEMP 폴더 내 빈 dir 파일이 있는 경우 하위 디렉토리까지 삭제
    dir_remove(temp_sample_list)


unzip_list=['7z','bz2','xz','tar','rar','Z','lz','sqlite','swf','gz','zip','ar','arj','xz']
def unzip_manager(temp_sample_list):
    #반복문을 통한 flag 설정
    
    while True:
        for temp_sample in temp_sample_list:
            unzip_sample(temp_sample)
        temp_sample_list=[os.path.join(c_c.PATH_TEMP,fname) for fname in [fname for fname in os.listdir(c_c.PATH_TEMP)]]
        #만약, 압축 해제 했는데 zip이 있다면 리스트가 있을 것이고, 없으면 빈리스트
        zip_list=[0 for temp_sample in temp_sample_list if filetype.guess(temp_sample) in unzip_list]
        if zip_list==[]:return temp_sample_list 


def unzip_sample(temp_sample_path,_password=None):
    dir_path=os.path.dirname(temp_sample_path)
    if os.path.isdir(temp_sample_path):return
    if os.path.exists(temp_sample_path)!=True:return
    kind=filetype.guess(temp_sample_path)
    def _zip():
        try:
            zFile=zipfile.ZipFile(temp_sample_path)
        except zipfile.BadZipFile:
            etc_unpack()
            return

        if _password:
            try:
                zFile.setpassword(_password)
            except:
                pass
        for zfile_name in zFile.namelist():
            #Temp 경로에 압축해제 압축해재시 압축파일 내부에 있는 이름으로 진행
            try:
                zFile.extract(zfile_name,dir_path)
            except:
                continue
            #Temp에 압축해제된 파일 풀 경로 설정
            #unpack_file_path=os.path.join(dir_path,zfile_name)
            #unpack_file_path_list.append(unpack_file_path)
        zFile.close()
        '''
        for unpack_file_path in unpack_file_path_list:
            if os.path.isfile(unpack_file_path):
                kind=filetype.guess(unpack_file_path)
                if kind!=None and kind in unzip_list:
                    unzip_sample(unpack_file_path,_password)
        '''
    def etc_unpack():
        #temp_sample_dir_path=temp_sample_path.split('.')[0]
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(4)
        try:
            Archive(temp_sample_path).extractall(c_c.PATH_TEMP)
        except:
            return

    def _unrar():
        rf = rarfile.RarFile(temp_sample_path)
        rf.extractall(path=c_c.PATH_TEMP,pwd=_password)    
    
    if kind!=None:
        
        if kind.extension=='zip':
            _zip()
        
        elif kind.extension=='rar':
            _unrar()
        elif kind.extension in unzip_list:
            etc_unpack()
        
        if kind.extension in unzip_list:
            try:
                os.remove(temp_sample_path)
            except:
                return 

def dir_remove(temp_sample_list):
    
    dir_list=list()
    for temp_sample in temp_sample_list:
        if temp_sample==c_c.PATH_TEMP:continue

        if os.path.isdir(temp_sample):
            dir_list.append(temp_sample)

    for dir_ in list(set(dir_list)):
        shutil.rmtree(dir_,ignore_errors=True)

def sample_move_extenstion(temp_sample):
    if os.path.isdir(temp_sample):return
    if os.path.exists(temp_sample)!=True:return

    kind = filetype.guess(temp_sample)
    if kind!=None:
        if kind in unzip_list:
            return

    ext_fname_path,ext_path=get_type(temp_sample)
    if ext_fname_path==None:
        shutil.move(temp_sample,os.path.join(c_c.PATH_OTHERS,os.path.basename(temp_sample)))
    else:
        if not os.path.exists(ext_path): 
            os.makedirs(ext_path)
        shutil.move(temp_sample,ext_fname_path)     







def dir_move_sample(temp_sample):
    if os.path.isdir(temp_sample):
        for root, dirs, files in os.walk(temp_sample):
            for file_ in files:
                shutil.move(os.path.join(root,file_),os.path.join(c_c.PATH_TEMP,file_))

def get_type(temp_sample_path):
    try:
        kind = filetype.guess(temp_sample_path)
    except OSError:
        return None, ''

    file_name=os.path.basename(temp_sample_path).split('.')[0]

    if kind==None:
        
        if len(os.path.basename(file_name).split('.'))>=2:
            ext=os.path.basename(file_name).split('.')[1].replace('.','')
            ext_path=os.path.join(c_c.PATH,ext)
            ext_fname_path=os.path.join(ext_path,file_name)
            return ext_fname_path,ext_path
        else:

            return None,''

    else:
        ext_path=os.path.join(c_c.PATH,kind.extension)
        ext_fname_path=os.path.join(ext_path,file_name)
        return ext_fname_path,ext_path