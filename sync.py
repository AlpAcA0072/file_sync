import socket
import struct
import os
import hashlib

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

ROOT_PATH = local path
PUSH_PATH = None
IP = 'Your remote IP'
PORT = remote port

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
            file = path + '\\' + file
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

def handleFile(file):
    conn.send(file.encode(encoding='utf-8'))
    print(conn.recv(1024).decode('utf-8'))

    md5 = getMd5(file)
    conn.send(md5.encode(encoding='utf-8'))
    print(conn.recv(1024).decode('utf-8'))

    msg = conn.recv(1024).decode("utf-8")
    if msg == 'False':
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
            handleFile(event.src_path)


if __name__ == '__main__':
    #socket连接
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((IP, PORT))
        print("连接到服务器")
    except :
        print ('连接不成功')
    conn.send(ROOT_PATH.encode('utf-8'))
    PUSH_PATH = conn.recv(1024).decode('utf-8')
    print("PUSH_PATH:" + PUSH_PATH)

    # 初始文件列表
    current_files = readDir(ROOT_PATH)

    # 实时文件夹监测
    event_handler = FileMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path=ROOT_PATH, recursive=True)
    observer.start()

    for _ in current_files:
        handleFile(_)

    observer.join()
