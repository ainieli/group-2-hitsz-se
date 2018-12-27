# -*- coding:utf-8 -*-
import paramiko

#  功能：上传文件
# 输入：sour_addr ：上传的文件的完整路径（字符串），如'./search.py'
#      des_addr保存到服务器的路径，默认是None，函数会自动将文件上传到/root/目录下，名字是上传的文件名
def put_file_server(sour_addr, des_addr = None):
    if des_addr is None:
        des_addr = sour_addr.split('/')[-1]  # 取传入文件的路径最后一个/ 后面的内容，如./search.py取search.py
        des_addr = '/root/' + des_addr
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(sour_addr, des_addr)
        transport.close()
        return True
    except:
        print('connect failed')
        return False

#  功能：下载文件
# 输入：download_file ：下载的文件要保存的完整路径（字符串），如'./2015.csv'
#      sour_addr  要下载的文件保存到服务器的路径，默认是在/root下面，函数会自动去/root/目录下查找2015.csv这个文件
def get_file_server(download_file, sour_addr = None):
    if sour_addr is None:
        sour_addr = download_file.split('/')[-1]
        sour_addr = '/root/' + sour_addr
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(sour_addr, download_file)
        transport.close()
        return True
    except:
        print('connect failed')
        return False


# sour_addr = './data/UserList.csv'
# put_file_server(sour_addr)


# download_file = './2018.csv'
# dir = './'
# get_file_server(download_file)