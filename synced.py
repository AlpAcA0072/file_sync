import socket
import struct
import os
import hashlib

IP = 'your remote IP'
PORT = remote port
ROOT_PATH = None
PUSH_PATH = remote path

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

def check_file_existence(file, md5):
    file = file_to_local(file)
    if os.path.exists(file):
        return getMd5(file) == md5
    return False

def file_to_local(file):
    local_file = file.replace(ROOT_PATH, '')
    local_file = PUSH_PATH + local_file
    return local_file

def make_recursive_folder(file):
    rela_path = file.replace(PUSH_PATH, '')
    rela_path = rela_path.split('\\')
    rela_path = rela_path[0:-1]
    curr_path = PUSH_PATH
    for _ in rela_path:
        if _ :
            curr_path = curr_path +'\\'+ _
            if not os.path.exists(curr_path):
                os.makedirs(curr_path)

if __name__ == '__main__':
    print("从端")
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((IP, PORT))
    mySocket.listen(10)
    print("等待连接....")
    conn, addr = mySocket.accept()
    ROOT_PATH = conn.recv(1024).decode('utf-8')
    print("ROOT_PATH:" + ROOT_PATH)
    conn.send(PUSH_PATH.encode('utf-8'))
    while True:
        file = conn.recv(1024).decode('utf-8')
        print("file: " + file)
        conn.send("file recieved.".encode('utf-8'))

        md5 = conn.recv(1024).decode('utf-8')
        print("md5: " + md5)
        conn.send("md5 recieved.".encode('utf-8'))

        file_exist = check_file_existence(file, md5)
        conn.send(str(file_exist).encode('utf-8'))
        if file_exist:
            continue
        # t = threading.Thread(target=recv_file, args=(conn, addr, file))
        # t.start()

        while 1:
            # 申请相同大小的空间存放发送过来的文件名与文件大小信息
            fileinfo_size = struct.calcsize('128sl')
            # 接收文件名与文件大小信息
            buf = conn.recv(fileinfo_size)
            # 判断是否接收到文件头信息
            if buf:
                filename, filesize = struct.unpack('128sl', buf)
                fn = filename.strip(b'\00')
                fn = fn.decode()
                print ('file new name is {0}, filesize is {1}'.format(str(fn),filesize))

                recvd_size = 0
                file = file_to_local(file)
                if os.path.exists(file):
                    os.remove(file)
                make_recursive_folder(file)
                fp = open(file, 'wb')
                print ('start receiving...')
            
                # 将分批次传输的二进制流依次写入到文件
                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        data = conn.recv(1024)
                        recvd_size += len(data)
                    else:
                        data = conn.recv(filesize - recvd_size)
                        recvd_size = filesize
                    fp.write(data)
                fp.close()
                print ('end receive...')
            break
