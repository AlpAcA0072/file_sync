import datetime
import json
import socket
import struct
import sys
import os
import shutil
import time
from threading import Thread, local
import hashlib
import shutil
from tkinter import CURRENT

import requests
import xlrd
from apscheduler.schedulers.blocking import BlockingScheduler
from requests_toolbelt import MultipartEncoder
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


CWD = os.getcwd()
# FILE_LIST = r'D:\test\fileList.txt'
# CONFIG_FILE = r'\config.txt'
ROOT_PATH = r'D:\test'
PUSH_PATH = None
IP = '127.0.0.1'
PORT = 1234


# 生成md5
def getMd5(file):
    m = hashlib.md5()
    with open(file, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)

    return m.hexdigest()


# 读取文件夹下所有文件（不限级）路径+名称+md5
def readDir(path):
    Files = []
    try:
        fileList = os.listdir(path)
        for file in fileList:
            file = path + '/' + file
            if os.path.isdir(file):
                subFiles = readDir(file)
                for _ in subFiles:
                    # 合并当前目录与子目录的所有文件路径
                    Files.append(_)
            else:
                Files.append(file)
        return Files
    except Exception as e:
        print(e)



# def getFiles():
#     # Files['name'] + Files['root'] 绝对路径
#     while not os.path.isfile(FILE_LIST):
#         print("Open slave end first!")
#         time.sleep(10)
#     Files = {}
#     Files['name'] = []  # 相对路径 + 文件名
#     Files['md5'] = []
#     Files['root'] = ''  # 根目录
#     with open(FILE_LIST, mode='r', encoding='utf-8') as f:
#         Files['root'] = f.readline()
#         line = f.readline()
#         while line:
#             Files['name'].append(line.split(',')[0])
#             Files['md5'].append(line.split(',')[1])
#     return Files

# def make_recursive_folder(recieve_path):
#     rela_path = recieve_path.replace(PUSH_URL, '')
#     rela_path = rela_path.split('/' )
#     rela_path = rela_path[0:-1]
#     curr_path = PUSH_URL
#     for _ in rela_path:
#         curr_path = curr_path +'/'+ _
#         if not os.path.exists(curr_path):
#             os.makedirs(curr_path)

# def test_copy_file(local_path):
#     recieve_path = PUSH_URL+local_path.replace(ROOT_PATH, '')
#     if os.path.isdir(recieve_path):
#         os.makedirs(recieve_path)
#     elif not os.path.exists(recieve_path):
#         make_recursive_folder(recieve_path)
#         # os.remove(recieve_path)
#         shutil.copyfile(local_path, recieve_path)       

def handleFile(file):
    # try:
    #     for i in range(len(REMAIN_FILES['name'])):
    #         # 推送文件
    #         # file_path = REMAIN_FILES['root'] + REMAIN_FILES['name'][i]
    #         # test_copy_file(REMAIN_FILES['name'][i])
            

    # except Exception as e:
    #     print(e)
    md5 = getMd5(file)
    conn.send(file.encode(encoding='utf-8'))
    conn.send(md5.encode(encoding='utf-8'))
    msg = conn.recv(1024).decode("utf-8")
    if msg:
        sendFile(file)

def sendFile(file):
    # 定义文件头信息，包含文件名和文件大小
    fhead = struct.pack('128sl', os.path.basename(file).encode('utf-8'), os.stat(file).st_size)
    # 发送文件名称与文件大小
    conn.send(fhead)

    # 将传输文件以二进制的形式分多次上传至服务器
    fp = open(file, 'rb')
    while 1:
        data = fp.read(1024)
        if not data:
            print ('{0} file send over...'.format(os.path.basename(file)))
            break
        conn.send(data)


# 实时监测文件夹变化
class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    # 重写文件改变函数，文件改变都会触发文件夹变化
    def on_modified(self, event):
        print("文件发生了变化: " + event.src_path)
        if os.path.isfile(event.src_path):
            # test_copy_file(event.src_path)
            handleFile()


# def comp(remoteList, curList):
#     for i in range(len(curList['name'])):
#         for j in range(len(remoteList['name'])):
#             if curList['md5'][i] == remoteList['md5'][j]:
#                 del curList['md5'][i]
#                 del curList['name'][i]
#     return curList


if __name__ == '__main__':
    #socket连接
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((IP, PORT))
        print("连接到服务器")
    except :
        print ('连接不成功')
    conn.send(PUSH_PATH.encode('utf-8'))
    PUSH_PATH = conn.recv(1024).decode('utf-8')
    print("PUSH_PATH:" + PUSH_PATH)

    # 初始文件列表
    # files = getFiles()
    # REMAIN_FILES = comp(curList=current_files, remoteList=files)
    # handle_file(ROOT_PATH, PUSH_URL, REMAIN_FILES)
    current_files = readDir(ROOT_PATH)
    for _ in current_files:
        handleFile(_)

    # 实时文件夹监测
    event_handler = FileMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path=ROOT_PATH, recursive=True)
    observer.start()
    observer.join()
