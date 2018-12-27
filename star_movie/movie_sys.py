# !/usr/bin/python
# -*- coding:utf-8 -*-
import idcode  # 将验证码生成模块的验证码值传入到本模块中
from server import get_file_server, put_file_server

import kivy.resources
from kivy.core.text import LabelBase
from kivy.config import Config
import random
import os
import getpass

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.listview import ListItemButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import mainthread
import kivy.resources
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import pylab as pl
from wordcloud import WordCloud, STOPWORDS

from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
from PIL import Image as image
from kivy.factory import Factory

import paramiko
import threading

from pygame import mixer

import hashlib

# 设定绘制的图片的像素和分辨率
plt.rcParams['savefig.dpi'] = 400  #图片像素
plt.rcParams['figure.dpi'] = 400   #分辨率
# 禁用多点触控(右键时不会出现小红点)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# 绘图注册字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False   # 减号的 Unicode 编码
font = {'weight': 'normal', 'size': 18}
font2 = {'weight': 'normal', 'size': 13}
# 加载字体资源
kivy.resources.resource_add_path(os.getenv('SystemDrive') + "\Windows\Fonts")
kivy.resources.resource_find("STKAITI.TTF")
# 注册字体
LabelBase.register("STKAITI_labelBase","STKAITI.TTF")
kivy.core.text.Label.register("STKAITI_label","STKAITI.TTF")
# 加载字体资源
kivy.resources.resource_find("FZSTK.TTF")
# 注册字体
LabelBase.register("FZSTK_labelBase","FZSTK.TTF")
kivy.core.text.Label.register("FZSTK_label","FZSTK.TTF")
# 加载字体资源
kivy.resources.resource_find("simhei.TTF")
# 注册字体
LabelBase.register("simhei_labelBase","simhei.TTF")
kivy.core.text.Label.register("simhei_label","simhei.TTF")


# 定义全局变量：用户名，密码，验证码，用户身份，
# 修改后的密码，确认密码，上一页id，验证答案，加载的用户列表全部内容，列表索引名
user_name = ''
password = ''
code = ''
identity = ''
password_change = ''
password_again = ''
last_page = ''
question1 = ''
question2 = ''
data = []
first_line = ''
# 定义一些全局量
lines_list_path = "./data/lines.csv"
user_list_path = './data/UserList.csv'
blank_plot_path = './pictures/blank.png'
user_list = {}  # 存储用户信息的列表
min_password_len = 6   # 定义最短密码长度
max_password_len = 16  # 定义最长密码长度
plots_to_export = []   # 定义导出图片名称列表
plots_to_export_checked = []  # 定义最终导出图片名称列表
search_history = []      # 定义搜索历史
years_to_crawl = []	   # 定义爬虫年份
# 窗口大小
firstpage_size = (600, 450)
register_size = (600, 400)
management_size = (560, 350)
login_size = (600, 350)
catalog_size = (600, 450)
scrapy_size = (600, 300)
history_size = (650, 400)
plot_size = (800, 600)
report_size = (600, 350)


# 密码加密
def encode(password):
	encoding = hashlib.md5()
	password_encode = password.encode(encoding='utf-8')
	encoding.update(password_encode)
	return encoding.hexdigest()
# 定义数据处理相关函数
def Emp_actors(data):
	data['film_actor'].fillna('无', inplace=True)
	return data
def Box_O_process(data):
	data_copy = data.copy()
	for i in range(len(data_copy)):
		each = list(data_copy['box_office'])[i]
		if '亿' in each:
			str_index = each.index('亿')
			data_copy.loc[i,'box_office'] = str(float(each[0:str_index]) * 10000)
	for i in range(len(data_copy)):
		each = list(data_copy['box_office'])[i]
		if '万' in each:
			str_index = each.index('万')
			data_copy.loc[i,'box_office'] = each[0:str_index]
	return data_copy
def read_data():
	pd.set_option('display.max_columns', 3)
	pd.set_option('display.max_rows', None)
	# 读文件和重新对column排序
	global data_2015
	global data_2016
	global data_2017
	global data_2018
	global all_data
	global col_key
	data_2015 = pd.read_csv(r'data\2015.csv', sep=',')
	data_2016 = pd.read_csv(r'data\2016.csv', sep=',')
	data_2017 = pd.read_csv(r'data\2017.csv', sep=',')
	data_2018 = pd.read_csv(r'data\2018.csv', sep=',')

	col_key = data_2018.columns
	year_delete4 = []
	for i in range(len(data_2018)):
		if list(data_2018['release_time'])[i][0:4] != '2018':
			year_delete4.append(i)
	for each in year_delete4:
		data_2018.drop([each], axis=0, inplace=True)
	data_2018 = pd.DataFrame(np.array(data_2018))
	data_2018.columns = col_key

	data_2015=Emp_actors(data_2015)
	data_2016=Emp_actors(data_2016)
	data_2017=Emp_actors(data_2017)
	data_2018=Emp_actors(data_2018)
	all_data = pd.concat([data_2015, data_2016, data_2017, data_2018])
	data_2015=Box_O_process(data_2015)
	data_2016=Box_O_process(data_2016)
	data_2017=Box_O_process(data_2017)
	data_2018=Box_O_process(data_2018)
	return


# 与服务器交互使用的函数，实现实时更新数据
# 函数功能：将服务器中的照片下载到本地./photo/2018/ 目录下，只会下载本地没有的
def updata_2018_data():
    local_photo_addr = './photo/2018/'
    local_data_addr = './data/2018.csv'
    remote_photo_dir = '/root/2018/scrapy-maoyan-board-master/crawler/crawler/2018/'
    remote_data_addr = '/root/2018/scrapy-maoyan-board-master/crawler/crawler/2018.csv'
    file_exist = os.listdir(local_photo_addr)
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)
        files = sftp.listdir(remote_photo_dir) # 获取远程图片目录
        for i in file_exist:
            i = i.replace('_',':')
            if i in files:
                files.remove(i)  # 删除本机已有
        for f in files:  # 下载本地没有的图片
            s = f.replace(':', '_')
            sftp.get(remote_photo_dir+f, local_photo_addr+s)
        print('本次更新了 ' + str(len(files)) + ' 张照片')
        # 覆盖本地2018.csv
        sftp.get(remote_data_addr, local_data_addr)
        transport.close()
    except:
        print('connect failed')
        return None
def spider_2018():
    try:
        ssh = paramiko.SSHClient()  # 创建SSH对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机
        ssh.connect(hostname='111.230.6.143', port=22, username='root', password='hitsz2019')  # 连接服务器
        stdin, stdout, stderr = ssh.exec_command(
            'cd 2018/scrapy-maoyan-board-master/crawler/crawler/ ; python3 main.py')  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
    except:
        print('connect failed')
        return None

def updata_2017_data():
    local_photo_addr = './photo/2017/'
    local_data_addr = './data/2017.csv'
    remote_photo_dir = '/root/2017/scrapy-maoyan-board-master/crawler/crawler/2017/'
    remote_data_addr = '/root/2017/scrapy-maoyan-board-master/crawler/crawler/2017.csv'
    file_exist = os.listdir(local_photo_addr)
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)
        files = sftp.listdir(remote_photo_dir) # 获取远程图片目录
        for i in file_exist:
            i = i.replace('_',':')
            if i in files:
                files.remove(i)  # 删除本机已有
        for f in files:  # 下载本地没有的图片
            s = f.replace(':', '_')
            sftp.get(remote_photo_dir+f, local_photo_addr+s)
        print('本次更新了 ' + str(len(files)) + ' 张照片')
        # 覆盖本地2017.csv
        sftp.get(remote_data_addr, local_data_addr)
        transport.close()
    except:
        print('connect failed')
        return None
def spider_2017():
    try:
        ssh = paramiko.SSHClient()  # 创建SSH对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机
        ssh.connect(hostname='111.230.6.143', port=22, username='root', password='hitsz2019')  # 连接服务器
        stdin, stdout, stderr = ssh.exec_command(
            'cd 2017/scrapy-maoyan-board-master/crawler/crawler/ ; python3 main.py')  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
    except:
        print('connect failed')
        return None
def updata_2016_data():
    local_photo_addr = './photo/2016/'
    local_data_addr = './data/2016.csv'
    remote_photo_dir = '/root/2016/scrapy-maoyan-board-master/crawler/crawler/2016/'
    remote_data_addr = '/root/2016/scrapy-maoyan-board-master/crawler/crawler/2016.csv'
    file_exist = os.listdir(local_photo_addr)
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)

        files = sftp.listdir(remote_photo_dir) # 获取远程图片目录
        for i in file_exist:
            i = i.replace('_',':')
            if i in files:
                files.remove(i)  # 删除本机已有
        for f in files:  # 下载本地没有的图片
            s = f.replace(':', '_')
            sftp.get(remote_photo_dir+f, local_photo_addr+s)
        print('本次更新了 ' + str(len(files)) + ' 张照片')
        # 覆盖本地2016.csv
        sftp.get(remote_data_addr, local_data_addr)
        transport.close()
    except:
        print('connect failed')
        return None
def spider_2016():
    try:
        ssh = paramiko.SSHClient()  # 创建SSH对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机
        ssh.connect(hostname='111.230.6.143', port=22, username='root', password='hitsz2019')  # 连接服务器
        stdin, stdout, stderr = ssh.exec_command(
            'cd 2016/scrapy-maoyan-board-master/crawler/crawler/ ; python3 main.py')  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
    except:
        print('connect failed')
        return None
def updata_2015_data():
    local_photo_addr = './photo/2015/'
    local_data_addr = './data/2015.csv'
    remote_photo_dir = '/root/2015/scrapy-maoyan-board-master/crawler/crawler/2015/'
    remote_data_addr = '/root/2015/scrapy-maoyan-board-master/crawler/crawler/2015.csv'
    file_exist = os.listdir(local_photo_addr)
    try:
        transport = paramiko.Transport(('111.230.6.143', 22))
        transport.connect(username='root', password='hitsz2019')
        sftp = paramiko.SFTPClient.from_transport(transport)
        files = sftp.listdir(remote_photo_dir) # 获取远程图片目录
        for i in file_exist:
            i = i.replace('_',':')
            if i in files:
                files.remove(i)  # 删除本机已有
        for f in files:  # 下载本地没有的图片
            s = f.replace(':', '_')
            sftp.get(remote_photo_dir+f, local_photo_addr+s)
        print('本次更新了 ' + str(len(files)) + ' 张照片')
        # 覆盖本地2015.csv
        sftp.get(remote_data_addr, local_data_addr)
        transport.close()
    except:
        print('connect failed')
        return None
def spider_2015():
    try:
        ssh = paramiko.SSHClient()  # 创建SSH对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机
        ssh.connect(hostname='111.230.6.143', port=22, username='root', password='hitsz2019')  # 连接服务器
        stdin, stdout, stderr = ssh.exec_command(
            'cd 2015/scrapy-maoyan-board-master/crawler/crawler/ ; python3 main.py')  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
    except:
        print('connect failed')
        return None
# 更新本地数据
def update(time):
    if '2015' in time:
        spider_2015()
        updata_2015_data()
    if '2016' in time:
        spider_2016()
        updata_2016_data()
    if '2017' in time:
        spider_2017()
        updata_2017_data()
    if '2018' in time:
        spider_2018()
        updata_2018_data()


#  输入photo_list，输出pdf
def convert_images_to_pdf(photo_list, pdf_path):
	img_path = './draw'
	pages = 0
	c = canvas.Canvas(pdf_path, pagesize=portrait(A4))
	c.setFont("Times-Roman", 20)
	c.drawCentredString(300, 800, 'The report of movie data')
	j = 0
	for i in photo_list:
		f = img_path + os.sep + str(i)
		img = image.open(f)
		(w0, h0) = img.size
		high = h0/(w0/400)
		if j % 2 == 0:
			c.drawImage(f, 100, 470, 400, high)
			j = j+1
		else:
			c.drawImage(f, 100, 100, 400, 300)
			c.showPage()
			pages = pages + 1
			j = j+1
	c.save()


# 以下为类定义
# 登录界面
class LogInGUI(Screen):
	# 定义类中变量：显示的消息，是否回显密码
	text = ''
	password_hide = True
	# 用户名查重
	def NameNotInList(self):
		global user_name
		if user_name in user_list.keys():
			LogInGUI.text = ''
			return False
		elif user_name == '':
			LogInGUI.text = '请输入一个用户名！'
			return True
		else:
			LogInGUI.text = '该用户尚未注册，请重试！'
			return True
	# 关键字保留
	def IsReservedKey(self):
		global user_name
		if user_name == 'visitor':  # 保留字不可作为用户名
			return True
		return False
	# 加载已经注册的用户列表，存入字典user_list中，键值为用户名，取值为密码，都取字符型
	def InitUserList(self):
		global user_list
		if get_file_server(user_list_path) == False:
			LogInGUI.text = '网络不可用'
			return False
		with open(user_list_path) as file:
			file.readline()				  # 文档第一行为维度名称，无需放入user_list
			for line in file:
				temp_list = line.rstrip('\n').split(',')  # 除掉\n，以逗号分隔用户名和密码
				user_list[temp_list[0]] = temp_list[1]	  # 将键值和值都取为字符型
		return True
	# 老用户登录，输入为用户名，密码，验证码
	def SuccessToLogIn(self):
		global user_name, password, code
		if code.lower() == idcode.result.lower():  # 验证码比较不区分大小写
			if user_name in user_list.keys():
				if encode(password) == user_list[user_name]:
					return True
			LogInGUI.text = '输入的用户名或密码有误，请重试！'
			return False
		LogInGUI.text = '输入的验证码有误，请重试！'
		return False
	# 获得框中的信息
	def GetText(self):
		global user_name, password, code
		user_name = str("{}".format(self.name_input.text))
		password = str("{}".format(self.password_input.text))
		code = str("{}".format(self.idcode_input.text))
	# 将消息打印在GUI界面上
	def ShowText(self):
		self.info.text = LogInGUI.text
	# 清除回显的消息
	def ClearInfo(self):
		self.info.text = ''
		return True
	# 重新加载验证码
	def LoadImage(self):
		idcode.CreateCode((200,100), 4, (255, 255, 255))
		self.image.reload()
	# 清空TextInput的内容
	def ClearTextInput(self):
		self.name_input.text = ''
		self.password_input.text = ''
		self.idcode_input.text = ''
	# 按钮控制是否显示密码
	def HidePassword(self):
		if LogInGUI.password_hide:
			LogInGUI.password_hide = False
		else:
			LogInGUI.password_hide = True
		self.password_input.password = LogInGUI.password_hide
	# 跳转下一页
	def NextPage(self, next):
		global last_page
		if next == 'management':
			Window.size = management_size
		elif next == 'catalog':
			Window.size = catalog_size
		elif next == 'firstpage':
			Window.size = firstpage_size
		self.manager.current = next
		last_page = 'login'
	# 将身份存入全局变量
	def SaveIndentity(self, id):
		global identity
		identity = id


# 目录
class Catalog(Screen):
	# 获得当前登录者身份
	def GetID(self):
		global identity
		return identity
	# 跳转下一页
	def NextPage(self, next_page):
		global last_page, plots_to_export, plots_to_export_checked, search_history
		if next_page == 'management':
			Window.size = management_size
		elif next_page == 'scrapy':
			Window.size = scrapy_size
		elif next_page == 'firstpage':
			plots_to_export = []
			plots_to_export_checked = []
			search_history = []
			Window.size = firstpage_size
		elif next_page == 'history':
			Window.size = history_size
		elif next_page == 'seventh':
			Window.size = report_size
		else:
			Window.size = plot_size
		self.manager.current = next_page
		last_page = 'catalog'
	def Music(self):
		global play_music, have_music
		if have_music:
			have_music = False
			play_music.pause()
		else:
			have_music = True
			play_music.unpause()


# 用户信息管理
class Management(Screen):
	text = ''
	# 页面跳转
	def NextPage(self, next_page):
		if next_page == 'catalog':
			Window.size = catalog_size
		self.manager.current = next_page
	# 获得框中的信息
	def GetText(self):
		global password_change, password_again, question1, question2
		password_change = str("{}".format(self.password_change_input.text))
		password_again = str("{}".format(self.password_again_input.text))
		question1 = str("{}".format(self.question_first.text))
		question2 = str("{}".format(self.question_second.text))
	# 在文件中修改用户信息
	def ChangeUserPassword(self,user_name, new_password):
		global data, first_line
		with open(user_list_path, 'r') as f:
			first_line = f.readline()
			data = f.readlines()
			for i in range(len(data)):
				line = data[i].rstrip('\n').split(',')
				if line[0] == user_name:
					data[i] = user_name + ',' + encode(new_password) + ',' + line[2] + ',' + line[3] + '\n'
					break
		with open(user_list_path, 'w') as f:
			f.write(first_line)
			f.writelines(data)
		if put_file_server(user_list_path):
			return True
		return False
	def IndentifyQuestion(self,user_name):
		global question1, question2, first_line, data
		with open(user_list_path, 'r') as f:
			first_line = f.readline()
			data = f.readlines()
			for i in range(len(data)):
				line = data[i].rstrip('\n').split(',')
				if line[0] == user_name:
					if encode(question1) == line[2] or encode(question2) == line[3]:
						return True
					return False
	# 确定回显信息
	def SuccessToChangePassword(self):
		global user_name, password_change, password_again
		if password_change != password_again:
			Management.text = '密码不一致，请重试！'
			return False
		if len(password_again) < min_password_len or len(password_again) > max_password_len:
			Management.text = '密码长度要求6-16位，请重试！'
			return False
		if not Management.IndentifyQuestion(self, user_name):
			Management.text = '验证问题错误，请重试！'
			return False
		else:
			Management.text = '修改成功！'
			# 写文件修改用户信息
			if Management.ChangeUserPassword(self, user_name, password_change):
				return True
			Management.text = '网络不可用'
			return False
	# 显示信息
	def ShowText(self):
		self.info.text = Management.text
		if Management.text == '修改成功！':
			self.info.color = [0, 1, 0, 1]  # 绿色
		else:
			self.info.color = [1, 0, 0, 1]  # 红色
	def ShowName(self):
		global identity
		self.user_name.text = identity
	# 清空输入框
	def ClearTextInput(self):
		self.password_again_input.text = ''
		self.password_change_input.text = ''
		self.question_first.text = ''
		self.question_second.text = ''
	# 清空名字，防止下次进入的时候还是上次的名字
	def ClearName(self):
		self.user_name.text = '点击"刷新"显示用户名'
		self.info.text = ''
	# 确定返回页
	def ReturnPage(self):
		global last_page
		if last_page == 'login':
			Window.size = login_size
			self.manager.current = 'login'
		elif last_page == 'catalog':
			Window.size = catalog_size
			self.manager.current = 'catalog'
		self.user_name.color = [0.5, 0.5, 0.5, 1]  # Label显示恢复默认的灰色


# 注册
class RegisterGUI(Screen):
	# 定义类中变量：显示的消息，是否回显密码
	text = ''
	password_hide = True
	# 跳转下一页
	def NextPage(self, next):
		if next == 'firstpage':
			Window.size = firstpage_size
		self.manager.current = next
	# 用户名查重
	def NameNotInList(self):
		global user_name
		if user_name in user_list.keys():
			return False
		else:
			return True
	# 关键字保留
	def IsReservedKey(self):
		global user_name
		if user_name == 'visitor':  # 保留字不可作为用户名
			return True
		return False
	# 密码至少六位，最长十六位
	def EnoughPasswordLength(self):
		global password
		if len(password) < min_password_len or len(password) > max_password_len:
			return False
		else:
			return True
	# 将新用户写入.csv文档
	def WriteBackUserList(self):
		global user_name, password, question1, question2
		file = open(user_list_path, 'a')  # 追加模式
		file.write(str(user_name) + ',' + str(encode(password)) + ',' + str(encode(question1)) + ',' + str(encode(question2)) + '\n')
		file.close()
		put_file_server(user_list_path)
	# 新用户注册
	def NewUser(self):
		global user_name, password, code, question1, question2
		# 没有输入用户名
		if user_name == '':
			RegisterGUI.text = '请输入一个用户名！'
			return False
		if RegisterGUI.NameNotInList(self) and not RegisterGUI.IsReservedKey(self):
			if RegisterGUI.EnoughPasswordLength(self):
				if question1 != '' and question2 != '':
					RegisterGUI.WriteBackUserList(self)
					RegisterGUI.text = '注册成功！'
					return True
				RegisterGUI.text = '请回答验证问题！'
				return False
			RegisterGUI.text = '密码长度要求6-16位，请重试！'
			return False
		RegisterGUI.text = '该用户已存在！'
		return False
	# 加载已经注册的用户列表，存入字典user_list中，键值为用户名，取值为密码，都取字符型
	def InitUserList(self):
		global user_list
		if get_file_server(user_list_path) == False:
			RegisterGUI.text = '网络不可用'
			return False
		with open(user_list_path) as file:
			file.readline()  # 文档第一行为维度名称，无需放入user_list
			for line in file:
				temp_list = line.rstrip('\n').split(',')  # 除掉\n，以逗号分隔用户名和密码
				user_list[temp_list[0]] = temp_list[1]	# 将键值和值都取为字符型
		return True
	# 获得框中的信息
	def GetText(self):
		global user_name, password, code, question1, question2
		user_name = str("{}".format(self.name_input.text))
		password = str("{}".format(self.password_input.text))
		question1 = str("{}".format(self.question_first.text))
		question2 = str("{}".format(self.question_second.text))
	# 将消息打印在GUI界面上
	def ShowText(self):
		self.info.text = RegisterGUI.text
		if RegisterGUI.text == '注册成功！':
			self.info.color = [0, 1, 0, 1]  # 绿色
		else:
			self.info.color = [1, 0, 0, 1]  # 红色
	# 清空TextInput的内容
	def ClearTextInput(self):
		self.name_input.text = ''
		self.password_input.text = ''
		self.question_first.text = ''
		self.question_second.text = ''
	# 按钮控制是否显示密码
	def HidePassword(self):
		if RegisterGUI.password_hide:
			RegisterGUI.password_hide = False
		else:
			RegisterGUI.password_hide = True
		self.password_input.password = RegisterGUI.password_hide


# 爬虫
class Scrapy(Screen):
	# 页面跳转
	def NextPage(self, next_page):
		if next_page == 'catalog':
			Window.size = catalog_size
		self.manager.current = next_page
	def add_years(self,text):
		global years_to_crawl
		if text not in years_to_crawl:
			years_to_crawl.append(text)
	def remove_years(self,text):
		global years_to_crawl
		if text in years_to_crawl:
			years_to_crawl.remove(text)
	def clear_everything(self):
		self.ids['2018'].state = 'normal'
		self.ids['2017'].state = 'normal'
		self.ids['2016'].state = 'normal'
		self.ids['2015'].state = 'normal'
		global years_to_crawl
		years_to_crawl = []


# 初始页
class FirstPage(Screen):
	lines = []
	classical_line = StringProperty()
	def __init__(self, **kwargs):
		super(FirstPage, self).__init__(**kwargs)
		self.lines = pd.read_csv(lines_list_path, encoding="utf-8")
		random_sequence = random.randint(0, 39)
		line = self.lines.loc[random_sequence]
		self.classical_line = line[1] + '\n——《' + line[0] + '》'
	# 跳转下一页
	def NextPage(self, next):
		if next == 'login':
			Window.size = login_size
		elif next == 'register':
			Window.size = register_size
		self.manager.current = next
	# 随机显示一句经典台词
	def ShowClassicalLines(self):
		random_sequence = random.randint(0, 39)
		line = self.lines.loc[random_sequence]
		self.classical_line = line[1] + '\n——《' + line[0] + '》'


# 搜索页
class SecondScreen(Screen):
	content=ObjectProperty()
	history=ObjectProperty()
	result_found=ObjectProperty()
	title=ObjectProperty()
	time=ObjectProperty()
	movie_genre=ObjectProperty()
	movie_grade=ObjectProperty()
	movie_director=ObjectProperty()
	movie_actors=ObjectProperty()
	movie_BoxOffice=ObjectProperty()
	result=[]
	result_dic={}
	# 跳转下一页
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def display_search_text(self,text):
		if self.ids['show_search_history'].state == 'down':
			self.content.text=text
	#不显示搜索历史
	def clear_history(self):
		self.history.item_strings =[]
		self.history.adapter.data.clear()
		self.history.adapter.data.extend([])
		self.history._trigger_reset_populate()
	#显示搜索历史
	def show_history(self):
		global search_history
		self.history.item_strings =[search_history]
		self.history.adapter.data.clear()
		self.history.adapter.data.extend(search_history)
		self.history._trigger_reset_populate()
	def show_search_result(self):
		self.result_found.item_strings =[self.result]
		self.result_found.adapter.data.clear()
		self.result_found.adapter.data.extend(self.result)
		self.result_found._trigger_reset_populate()
	def clear_search_result(self):
		self.result_found.item_strings =[]
		self.result_found.adapter.data.clear()
		self.result_found.adapter.data.extend([])
		self.result_found._trigger_reset_populate()
	def show_details(self,text):
		self.title.text=str(self.result_dict[text][0])
		self.time.text=str(self.result_dict[text][1])
		self.movie_genre.text=str(self.result_dict[text][2])
		self.movie_grade.text=str(self.result_dict[text][3])
		self.movie_director.text=str(self.result_dict[text][4])
		self.movie_actors.text=str(self.result_dict[text][5])
		self.movie_BoxOffice.text=str(self.result_dict[text][6])
		if os.path.exists('./photo/' + self.time.text[0:4] + '/' + text + '.jpg'):
			self.ids['image'].source = './photo/' + self.time.text[0:4] + '/' + text + '.jpg'
		else:
			self.ids['image'].source = blank_plot_path
	#清空内容
	def show_empty(self):
		self.title.text = ''
		self.time.text = ''
		self.movie_genre.text = ''
		self.movie_grade.text = ''
		self.movie_director.text = ''
		self.movie_actors.text = ''
		self.movie_BoxOffice.text = ''
		self.ids['image'].source = blank_plot_path
	#显示用户所选排序方式
	def display_sort(self,text):
		if self.ids['show_sort_selection'].state == 'down':
			self.sort_way.text=text
	#显示搜索结果排序方式
	def show_sort_selection(self):
		selection=["评分降序（默认）","票房降序"]
		self.sort_list_selection.item_strings =[selection]
		self.sort_list_selection.adapter.data.clear()
		self.sort_list_selection.adapter.data.extend(selection)
		self.sort_list_selection._trigger_reset_populate()
	#隐藏搜索结果排序方式
	def clear_sort_selection(self):
		self.sort_list_selection.item_strings =[]
		self.sort_list_selection.adapter.data.clear()
		self.sort_list_selection.adapter.data.extend([])
		self.sort_list_selection._trigger_reset_populate()
	#搜索函数
	def Searchinfo(self,search_content, sort_by="score", sequence=False):
		global all_data, search_history
		all_data = all_data.reset_index(drop=True)
		search_history.insert(0, search_content)
		# 输入字符串预处理
		search_content = search_content.replace('*', '')
		if len(search_content) == 0:
			return None
		# 寻找查找内容
		search_result = all_data[(all_data['film_actor'].str.contains(search_content)) |
		(all_data['film_director'].str.contains(search_content)) |
		(all_data['film_theme'].str.contains(search_content)) |
		(all_data['film_name'].str.contains(search_content))]
		# 如果没有找到，返回空和历史记录
		if search_result.shape[0] == 0:
			return None
		# 否则将搜索结果按照输入排序
		else:
			# 若选择按照票房降序排序
			if self.sort_way.text=='票房降序':
				sort_by = "box_office"
			# 否则按照默认评分降序排序
				box_office = search_result['box_office'].copy()
				for i in box_office.index:
					if box_office[i][-1] == '万':
						box_office[i] = float(box_office[i][0:-1])
					else:
						box_office[i] = float(box_office[i][0:-1]) * 10000
				box_office = box_office.sort_values(ascending=sequence)
				order = list(box_office.index)
				search_result = search_result.loc[order, :]
			else:
				search_result = search_result.sort_values(sort_by, ascending=sequence)
			columes_order = ['film_name', 'release_time', 'film_theme', 'score', 'film_director', 'film_actor',
							 'box_office']
			search_result = search_result[columes_order]
			fin_result = np.array(search_result)
			fin_result = fin_result.tolist()  # 转到list
			fin_result_dic = {}
			for item in fin_result:  # list转dict
				fin_result_dic[item[0]] = item
			#更新search_result list view 内容
			self.result= list(fin_result_dic.keys())
			self.show_search_result()
			self.result_dict=fin_result_dic
			return fin_result_dic
	# 退出页面时清空所有内容
	def clear_everything(self):
		self.ids['search_box'].text=''
		self.ids['sort_by'].text=''
		self.result=[]
		self.ids['show_search_history'].state='normal'
		self.ids['show_sort_selection'].state='normal'
		self.clear_sort_selection()
		self.clear_history()
		self.clear_search_result()
		self.show_empty()


#题材与票房界面
class ThirdScreen(Screen):
	current_title=''
	search_year_start = ObjectProperty()
	search_season = ObjectProperty()
	search_month = ObjectProperty()
	year_text=ObjectProperty()
	months=''
	# 跳转下一页
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def display_selected_end_year(self,text):
		self.search_year_end.text = text
	def show_start_year_selection(self):
		years=["2018","2017","2016","2015"]
		self.year_results_start.item_strings = years
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend(years)
		self.year_results_start._trigger_reset_populate()
	def clear_start_year_selection(self):
		self.year_results_start.item_strings =[]
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend([])
		self.year_results_start._trigger_reset_populate()
	def show_season_selection(self):
		seasons=["1","2","3","4","全部"]
		self.season_results.item_strings = seasons
		self.season_results.adapter.data.clear()
		self.season_results.adapter.data.extend(seasons)
		self.season_results._trigger_reset_populate()
	def clear_season_selection(self):
		self.season_results.item_strings =[]
		self.season_results.adapter.data.clear()
		self.season_results.adapter.data.extend([])
		self.season_results._trigger_reset_populate()
	def search_for_month(self,season):
		self.search_month.text=""
		season_month={"1":["1","2","3","全部"],"2":["4","5","6",'全部'],"3":["7","8","9",'全部'],"4":["10","11","12",'全部'],"":[],"全部":["全部"]}
		self.months=season_month[season]
		if self.ids['show_month'].state == 'down':
			self.show_month_selection()
	def show_month_selection(self):
		self.month_results.item_strings = self.months
		self.month_results.adapter.data.clear()
		self.month_results.adapter.data.extend(self.months)
		self.month_results._trigger_reset_populate()
	def clear_month_selection(self):
		self.month_results.item_strings =[]
		self.month_results.adapter.data.clear()
		self.month_results.adapter.data.extend([])
		self.month_results._trigger_reset_populate()
	def show_funtion(self,text):
		self.ids["function"].text=text
	def change_start_year_text(self,text):
		if self.ids['show_start_year'].state == 'down':
			self.search_year_start.text=text
	def change_end_year_text(self,text):
		if self.ids['show_end_year_selection'].state == 'down':
			self.search_year_end.text=text
	def change_season_text(self,text):
		if self.ids['show_season'].state == 'down':
			self.search_season.text=text
	def change_month_text(self,text):
		if self.ids['show_month'].state == 'down':
			self.search_month.text=text
	#各题材电影票房份额绘图
	def FilmTheme_BoxOffice(self, type, year, quarter, month):
		data = []
		if str(year) == '2015':
			data = data_2015
		elif str(year) == '2016':
			data = data_2016
		elif str(year) == '2017':
			data = data_2017
		elif str(year) == '2018':
			data = data_2018
		dict_theme = {}
		if str(quarter) == '全部':
		# 绘制所选年份的票房图表：
			movie_type = list(data['film_theme'])
			count = 0
			for each in movie_type:
				each_type = each.split(',')
				for i in each_type:
					if i not in dict_theme.keys():
						dict_theme[i] = int(float(data['box_office'][count]))
					else:
						dict_theme[i] += int(float(data['box_office'][count]))
				count += 1
		elif str(month) == '全部':
		# 按季度划分并绘制图表：
			month_list = []
			if str(quarter) == '1':
				month_list = ['01', '02', '03']
			if str(quarter) == '2':
				month_list = ['04', '05', '06']
			if str(quarter) == '3':
				month_list = ['07', '08', '09']
			if str(quarter) == '4':
				month_list = ['10', '11', '12']
			quarter_index = []
			for i in range(len(data)):
				for each in month_list:
					if list(data['release_time'])[i][5:7] == each:
						quarter_index.append(i)
			quarter_data = data.loc[quarter_index]
			quarter_data = pd.DataFrame(np.array(quarter_data))
			quarter_data.columns = col_key
			movie_type = list(quarter_data['film_theme'])
			count = 0
			for each in movie_type:
				each_type = each.split(',')
				for i in each_type:
					if i not in dict_theme.keys():
						dict_theme[i] = int(float(quarter_data['box_office'][count]))
					else:
						dict_theme[i] += int(float(quarter_data['box_office'][count]))
				count += 1
		else:
		# 按月份绘制票房图表：
			month_index = []
			if len(str(month)) == 1:
				for i in range(len(data)):
					if list(data['release_time'])[i][5:7] == '0'+str(month):
						month_index.append(i)
			else:
				for i in range(len(data)):
					if list(data['release_time'])[i][5:7] == str(month):
						month_index.append(i)
			month_data = data.loc[month_index]
			month_data = pd.DataFrame(np.array(month_data))
			month_data.columns = col_key
			movie_type = list(month_data['film_theme'])
			count = 0
			for each in movie_type:
				each_type = each.split(',')
				for i in each_type:
					if i not in dict_theme.keys():
						dict_theme[i] = int(float(month_data['box_office'][count]))
					else:
						dict_theme[i] += int(float(month_data['box_office'][count]))
				count += 1
		if '剧情' in dict_theme.keys():
			dict_theme.pop('剧情')
		dict_theme = sorted(dict_theme.items(), key=lambda d: d[1], reverse=True)
		Five_top_theme = []
		Five_theme_BoxOffice = []
		if len(dict_theme) >= 5:
			for i in range(5):
				Five_top_theme.append(list(dict_theme[i])[0])
				Five_theme_BoxOffice.append(list(dict_theme[i])[1])
			if str(quarter) == '全部':
				title = str(year) + "年" + "的题材票房比例" + type
			elif str(month) == '全部':
				title = str(year) + "年第" + str(quarter) + "季度题材票房比例" + type
			else:
				title = str(year) + "年" + str(month) + "月题材票房比例" + type
			if type == '条形图':
				color = ['yellow','gold','orange','navy','indigo']
				plt.bar(Five_top_theme, Five_theme_BoxOffice, color=color, width=0.6)
				for a, b in zip(Five_top_theme, Five_theme_BoxOffice):
					plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('票房/万元', font2)
				plt.xlabel('电影类型', font2)
			if type == '饼图':
				color = ['lightsalmon', 'lightgray', 'lightgreen', 'plum', 'paleturquoise']
				explode = [0.15, 0, 0, 0, 0]   # 设置与中心点的距离（此处将第一块分开）
				plt.axes(aspect=1)
				plt.title(title, font)
				plt.pie(x=Five_theme_BoxOffice, labels=Five_top_theme, explode=explode, autopct='%3.2f %%', shadow=True, labeldistance=0.8, startangle=90, pctdistance=0.6, colors=color)
				ax = plt.gca()
				box = ax.get_position()
				ax.set_position([box.x0, box.y0, box.width, box.height])
				ax.legend(bbox_to_anchor=(0.901, 1), ncol=1)    # 设置饼图的图例
			if type == '词云':
				plt.title(title)
				# font_path = r'C:\Windows\Fonts\msyh.ttf'
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										#random_state=50,
										stopwords=STOPWORDS).generate_from_frequencies(dict(dict_theme))
				plt.imshow(mycloudword)
				plt.axis("off")
			plt.savefig('draw/' + title + '.jpg', format='jpg')
			plt.close()
		else:
			print("Not have enough film theme!")
	def FilmTheme_BoxOffice_title(self, type, year, quarter, month):
		if str(quarter) == '全部':
			title = str(year) + "年" + "的题材票房比例" + type
		elif str(month) == '全部':
			title = str(year) + "年第" + str(quarter) + "季度题材票房比例" + type
		else:
			title = str(year) + "年" + str(month) + "月题材票房比例" + type
		return title
	def FilmTheme_BoxOffice_plot(self):
		plot_title=self.FilmTheme_BoxOffice_title(self.ids['function'].text,self.search_year_start.text,self.search_season.text,self.search_month.text)
		self.FilmTheme_BoxOffice(self.ids['function'].text, self.search_year_start.text, self.search_season.text, self.search_month.text)
		self.ids['picture'].source='./draw/' + plot_title+'.jpg'
		self.ids['picture'].reload()
		self.current_title = plot_title
	def current_plot_export(self):
		global plots_to_export
		if self.current_title=='':
			NoPlotYet().open()
		else:
			if self.current_title not in plots_to_export:
				plots_to_export.append(self.current_title)
			Exported().open()
	def clear_everything(self):
		self.ids['which_year_start'].text=''
		self.ids['which_season'].text=''
		self.ids['which_month'].text=''
		self.ids['function'].text=''
		self.ids['show_start_year'].state='normal'
		self.ids['show_season'].state='normal'
		self.ids['show_month'].state='normal'
		self.clear_start_year_selection()
		self.clear_season_selection()
		self.clear_month_selection()
		self.ids['pie chart'].state='normal'
		self.ids['word cloud'].state='normal'
		self.ids['bar plot'].state='normal'
		self.ids['picture'].source=blank_plot_path


#票房走势界面
class FourthScreen(Screen):
	search_year_start = ObjectProperty()
	search_season = ObjectProperty()
	search_month = ObjectProperty()
	year_text=ObjectProperty()
	end_year=StringProperty()
	months=''
	end_years=[]
	current_title=''
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def on_end_year(self):
		self.search_year_end.text = text
	def display_selected_end_year(self,text):
		self.search_year_end.text = text
	def show_start_year_selection(self):
		years=["2018","2017","2016","2015"]
		self.year_results_start.item_strings = years
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend(years)
		self.year_results_start._trigger_reset_populate()
	def clear_start_year_selection(self):
		self.year_results_start.item_strings =[]
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend([])
		self.year_results_start._trigger_reset_populate()
	def search_for_end_year(self,start_year):
		self.search_year_end.text=""
		start_end={"2015":["2015","2016","2017","2018"],"2016":["2016","2017","2018"],"2017":["2017","2018"],"2018":["2018"],"":[]}
		self.end_years=start_end[start_year]
		if self.ids['show_end_year_selection'].state == 'down':
			self.show_end_year_selection()
	def show_end_year_selection(self):
		self.year_results_end.item_strings = self.end_years
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend(self.end_years)
		self.year_results_end._trigger_reset_populate()
	def clear_end_year_selection(self):
		self.year_results_end.item_strings =[]
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend([])
		self.year_results_end._trigger_reset_populate()
	def show_season_selection(self):
		seasons=["Spring","Summer","Autumn","Winter","All"]
		self.season_results.item_strings = seasons
		self.season_results.adapter.data.clear()
		self.season_results.adapter.data.extend(seasons)
		self.season_results._trigger_reset_populate()
	def clear_season_selection(self):
		self.season_results.item_strings =[]
		self.season_results.adapter.data.clear()
		self.season_results.adapter.data.extend([])
		self.season_results._trigger_reset_populate()
	def search_for_month(self,season):
		self.search_month.text=""
		season_month={"Spring":["1","2","3"],"Summer":["4","5","6"],"Autumn":["7","8","9"],"Winter":["10","11","12"],"":[],"All":["All"]}
		self.months=season_month[season]
		if self.ids['show_month'].state == 'down':
			self.show_month_selection()
	def show_month_selection(self):
		self.month_results.item_strings = self.months
		self.month_results.adapter.data.clear()
		self.month_results.adapter.data.extend(self.months)
		self.month_results._trigger_reset_populate()
	def clear_month_selection(self):
		self.month_results.item_strings =[]
		self.month_results.adapter.data.clear()
		self.month_results.adapter.data.extend([])
		self.month_results._trigger_reset_populate()
	def show_funtion(self,text):
		self.ids["function"].text=text
	def change_start_year_text(self,text):
		if self.ids['show_start_year'].state == 'down':
			self.search_year_start.text=text
	def change_end_year_text(self,text):
		if self.ids['show_end_year_selection'].state == 'down':
			self.search_year_end.text=text
	def Year_BoxOffice(self, type, start_year, end_year):
		year_quarter_sum = []	# 每一年每一季度的票房和
		data_all_list = [data_2015, data_2016, data_2017, data_2018]
		for i in range(4):
			data = data_all_list[i]
			quarter_list = [['01', '02', '03'], ['04', '05', '06'], ['07', '08', '09'], ['10', '11', '12']]
			quarter_sum = []
			for j in range(len(quarter_list)):
				quarter_index = []
				for k in range(3):
					for each in quarter_list[j]:
						for i in range(len(data)):
							if list(data['release_time'])[i][5:7] == each:
								quarter_index.append(i)
				quarter_data = data.loc[quarter_index]
				sum_all = 0
				for value in quarter_data['box_office']:
					sum_all += int(float(value))
				quarter_sum.append(sum_all)
			year_quarter_sum.append(quarter_sum)
		if type == '折线图':
			quarter_num = ['1', '2', '3', '4']
			if start_year < end_year:
				title = str(start_year) + "-" + str(end_year) + "年每季度电影票房变化趋势" + type
				plt.title(title)
				color = ['salmon', 'deepskyblue', 'limegreen', 'orchid']
				for i in range((int(end_year)-int(start_year))+1):
					plt.plot(quarter_num, year_quarter_sum[int(start_year)-2015+i], color[i], label=str(int(start_year)+i), marker='o', ms=8)
				plt.legend(loc='upper right')
			else:
				title = str(start_year) + "年每季度电影票房变化趋势" + type
				plt.title(title)
				plt.plot(quarter_num, year_quarter_sum[int(start_year)-2015], color='deepskyblue', label=str(start_year), marker='o', ms=8)
				plt.legend(loc='upper right')
			plt.xlabel('季度', font2)
			plt.ylabel('票房/万元', font2)
			plt.savefig('draw/' + title + '.jpg', format='jpg')
			plt.close()
		if type == '箱线图':
			data_BoxOffice = []
			for each_data in data_all_list:
				data_BoxOffice.append(each_data['box_office'])
			if start_year == end_year:
				title = str(start_year) + "年电影票房-箱线图统计"
				plt.title(title, font)
				Data_BoxOffice = pd.DataFrame(data_BoxOffice[int(start_year) - 2015])
				Data_BoxOffice['box_office'] = Data_BoxOffice['box_office'].astype(float)
				Data_BoxOffice['box_office'] = Data_BoxOffice['box_office'].astype(int)
				Data_BoxOffice.columns = [str(start_year)]
				#colors = dict(boxes='DarkGreen', whiskers='DarkOrange', medians='DarkBlue', caps='Gray')
				Data_BoxOffice.boxplot(sym='r*', patch_artist=False, meanline=False, showmeans=True)
			else:
				title = str(start_year) + "-" + str(end_year) + "年电影票房-箱线图统计"
				plt.title(title, font)
				All_B_Office = []
				for i in range((int(end_year) - int(start_year)) + 1):
					B_Office = data_BoxOffice[int(start_year)-2015+i]
					B_Office = pd.DataFrame(B_Office)
					B_Office['box_office'] = B_Office['box_office'].astype(float)
					B_Office['box_office'] = B_Office['box_office'].astype(int)
					B_Office.columns = [str(int(start_year)+i)]
					All_B_Office.append(B_Office)
				result = pd.concat(All_B_Office)
				result.boxplot(sym='r*', patch_artist=False, meanline=False, showmeans=True)
			plt.ylabel("票房/万元")
			plt.savefig('draw/' + title + '.jpg', format='jpg')
			plt.close()
	def Year_BoxOffice_title(self, type, start_year, end_year):
		if type == '折线图':
			if start_year < end_year:
				title = str(start_year) + "-" + str(end_year) + "年每季度电影票房变化趋势" + type
			else:
				title = str(start_year) + "年每季度电影票房变化趋势" + type
		else:   # 箱线图
			if start_year == end_year:
				title = str(start_year) + "年电影票房-箱线图统计"
			else:
				title = str(start_year) + "-" + str(end_year) + "年电影票房-箱线图统计"
		return title
	def Year_BoxOffice_plot(self):
		plot_title=self.Year_BoxOffice_title(self.ids['function'].text,self.search_year_start.text,self.search_year_end.text)
		self.Year_BoxOffice(self.ids['function'].text,self.search_year_start.text,self.search_year_end.text)
		self.ids['picture'].source= './draw/' + plot_title+'.jpg'
		self.ids['picture'].reload()
		self.current_title=plot_title
	def current_plot_export(self):
		global plots_to_export
		if self.current_title=='':
			print("currently no plot")
			NoPlotYet().open()
		else:
			if self.current_title not in plots_to_export:
				plots_to_export.append(self.current_title)
			Exported().open()
	def clear_everything(self):
		self.ids['which_year_start'].text=''
		self.ids['which_year_end'].text=''
		self.ids['show_start_year'].state='normal'
		self.ids['show_end_year_selection'].state='normal'
		self.clear_start_year_selection()
		self.clear_end_year_selection()
		self.ids['function'].text=''
		self.ids['picture'].source=blank_plot_path
		self.ids['line chart'].state='normal'
		self.ids['box plot'].state='normal'


#top演员界面
class FifthScreen(Screen):
	search_year_start = ObjectProperty()
	search_year_end = ObjectProperty()
	sorting_way = ObjectProperty()
	top_way = ObjectProperty()
	year_text=ObjectProperty()
	end_year=StringProperty()
	months=''
	end_years=[]
	current_title=''
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def show_funtion(self,text):
		self.ids["function"].text=text
	def change_start_year_text(self,text):
		if self.ids['show_start_year'].state == 'down':
			self.search_year_start.text=text
	def change_end_year_text(self,text):
		if self.ids['show_end_year_selection'].state == 'down':
			self.search_year_end.text=text
	def change_sorting_text(self,text):
		if self.ids['show_sorting_way'].state == 'down':
			self.sorting_way.text=text
	def change_top_text(self,text):
		if self.ids['show_top_way'].state == 'down':
			self.top_num.text=text
	def on_end_year(self):
		self.search_year_end.text = text
	def display_selected_end_year(self,text):
		self.search_year_end.text = text
	def show_start_year_selection(self):
		years=["2018","2017","2016","2015"]
		self.year_results_start.item_strings = years
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend(years)
		self.year_results_start._trigger_reset_populate()
	def clear_start_year_selection(self):
		self.year_results_start.item_strings =[]
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend([])
		self.year_results_start._trigger_reset_populate()
	def search_for_end_year(self,start_year):
		self.search_year_end.text=""
		start_end={"2015":["2015","2016","2017","2018"],"2016":["2016","2017","2018"],"2017":["2017","2018"],"2018":["2018"],"":[]}
		self.end_years=start_end[start_year]
		if self.ids['show_end_year_selection'].state == 'down':
			self.show_end_year_selection()
	def show_end_year_selection(self):
		self.year_results_end.item_strings = self.end_years
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend(self.end_years)
		self.year_results_end._trigger_reset_populate()
	def clear_end_year_selection(self):
		self.year_results_end.item_strings =[]
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend([])
		self.year_results_end._trigger_reset_populate()
	def show_sorting_selection(self):
		selection=["按总票房","按出演次数","按平均评分"]
		self.sorting_selections.item_strings =[selection]
		self.sorting_selections.adapter.data.clear()
		self.sorting_selections.adapter.data.extend(selection)
		self.sorting_selections._trigger_reset_populate()
	def clear_sorting_selection(self):
		self.sorting_selections.item_strings =[]
		self.sorting_selections.adapter.data.clear()
		self.sorting_selections.adapter.data.extend([])
		self.sorting_selections._trigger_reset_populate()
	def show_top_selection(self):
		selection=['3','5','10']
		self.top_selections.item_strings =[selection]
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend(selection)
		self.top_selections._trigger_reset_populate()
	def clear_top_selection(self):
		self.top_selections.item_strings =[]
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend([])
		self.top_selections._trigger_reset_populate()
	def Top_movie_actors(self, type, start_year, end_year, top_num, attribute):
		data_all_list = [data_2015, data_2016, data_2017, data_2018]
		data = []
		if start_year == end_year:
			if str(start_year) == '2015':
				data = data_2015
			elif str(start_year) == '2016':
				data = data_2016
			elif str(start_year) == '2017':
				data = data_2017
			elif str(start_year) == '2018':
				data = data_2018
		elif start_year < end_year:
			data_list = data_all_list[(int(start_year)-2015):(int(end_year)-2015+1)]
			data = pd.concat(data_list, ignore_index=True)
		else:
			print("The order of the year selection is incorrect!")
			return
		#color = ['yellow', 'gold', 'orange', 'navy', 'indigo', 'red', 'blue', 'green', 'm', 'black']
		if attribute != '按出演次数':
			if start_year == end_year:
				title = str(start_year) + "年参演电影" + attribute + "前" + str(top_num) + "的演员" + type
			else:
				title = str(start_year) + '-' + str(end_year) + "年参演电影" + attribute + "前" + str(top_num) + "的演员" + type
		else:
			if start_year == end_year:
				title = str(start_year) + "年出演次数前" + str(top_num) + "的劳模演员" + type
			else:
				title = str(start_year) + '-' + str(end_year) + "年出演次数前" + str(top_num) + "的劳模演员" + type
		if attribute == '按总票房':
			dict_BoxOffice = {}
			movie_actors = list(data['film_actor'])
			count = 0
			for each in movie_actors:
				each_actor = str(each).split(',')
				for i in each_actor:
					if i not in dict_BoxOffice.keys():
						dict_BoxOffice[i] = int(float(data['box_office'][count]))
					else:
						dict_BoxOffice[i] += int(float(data['box_office'][count]))
				count += 1
			if '无' in dict_BoxOffice.keys():
				dict_BoxOffice.pop('无')
			dict_BoxOffice = sorted(dict_BoxOffice.items(), key=lambda d: d[1], reverse=True)   # 由字典变为了列表形式
			if type == '条形图':
				top_actors_list = []
				top_BoxO_list = []
				if str(top_num) == '3':
					color3 = ['darkorange', 'c', 'limegreen']
					for i in range(3):
						top_actors_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_actors_list, top_BoxO_list, color=color3, width=0.35)
					for a, b in zip(top_actors_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '5':
					color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
					for i in range(5):
						top_actors_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_actors_list, top_BoxO_list, color=color5, width=0.6)
					pl.xticks(rotation=30, size=8.5)
					for a, b in zip(top_actors_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '10':
					color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
							   'royalblue', 'b', 'darkblue']
					for i in range(10):
						top_actors_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_actors_list, top_BoxO_list, color=color10, width=0.7)
					pl.xticks(rotation=60, size=8)
					for a, b in zip(top_actors_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('票房/万元', font2)
			if type == '词云图':
				plt.title(title)
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										# random_state=50,
										stopwords=STOPWORDS)
				if str(top_num) == '3':
					dict_BoxOffice = dict_BoxOffice[0:3]
				if str(top_num) == '5':
					dict_BoxOffice = dict_BoxOffice[0:5]
				if str(top_num) == '10':
					dict_BoxOffice = dict_BoxOffice[0:10]
				plt.imshow(mycloudword.generate_from_frequencies(dict(dict_BoxOffice)))
				plt.axis("off")
		if attribute == '按平均评分':
			dict_count = {}
			movie_actors = list(data['film_actor'])
			for each in movie_actors:
				each_actor = str(each).split(',')
				for i in each_actor:
					if i not in dict_count.keys():
						dict_count[i] = 1
					else:
						dict_count[i] += 1

			dict_score = {}
			movie_actors = list(data['film_actor'])
			count = 0
			for each in movie_actors:
				each_actor = str(each).split(',')
				for i in each_actor:
					if i not in dict_score.keys():
						dict_score[i] = float(data['score'][count])
					else:
						dict_score[i] += float(data['score'][count])
				count += 1

			for i in dict_score.keys():
				dict_score[i] = round(dict_score[i] / dict_count[i], 2)


			if '无' in dict_score.keys():
				dict_score.pop('无')
			dict_score = sorted(dict_score.items(), key=lambda d: d[1], reverse=True)
			if type == '条形图':
				top_actors_list = []
				top_score_list = []
				if str(top_num) == '3':
					color3 = ['darkorange', 'c', 'limegreen']
					for i in range(3):
						top_actors_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_actors_list, top_score_list, color=color3, width=0.35)
					for a, b in zip(top_actors_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '5':
					color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
					for i in range(5):
						top_actors_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_actors_list, top_score_list, color=color5, width=0.6)
					pl.xticks(rotation=30, size=8.5)
					for a, b in zip(top_actors_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '10':
					color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
							   'royalblue', 'b', 'darkblue']
					for i in range(10):
						top_actors_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_actors_list, top_score_list, color=color10, width=0.7)
					pl.xticks(rotation=60, size=8)
					for a, b in zip(top_actors_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('评分/分数', font2)
			if type == '词云图':
				plt.title(title)
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										# random_state=50,
										stopwords=STOPWORDS)
				if str(top_num) == '3':
					dict_score = dict_score[0:3]
				if str(top_num) == '5':
					dict_score = dict_score[0:5]
				if str(top_num) == '10':
					dict_score = dict_score[0:10]
				plt.imshow(mycloudword.generate_from_frequencies(dict(dict_score)))
				plt.axis("off")
		if attribute == '按出演次数':
			dict_count = {}
			movie_actors = list(data['film_actor'])
			for each in movie_actors:
				each_actor = str(each).split(',')
				for i in each_actor:
					if i not in dict_count.keys():
						dict_count[i] = 1
					else:
						dict_count[i] += 1

			if '无' in dict_count.keys():
				dict_count.pop('无')
			dict_count = sorted(dict_count.items(), key=lambda d: d[1], reverse=True)
			if type == '条形图':
				top_actors_list = []
				top_count_list = []
				if str(top_num) == '3':
					color3 = ['darkorange', 'c', 'limegreen']
					for i in range(3):
						top_actors_list.append(list(dict_count[i])[0])
						top_count_list.append(list(dict_count[i])[1])
					plt.bar(top_actors_list, top_count_list, color=color3, width=0.35)
					for a, b in zip(top_actors_list, top_count_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '5':
					color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
					for i in range(5):
						top_actors_list.append(list(dict_count[i])[0])
						top_count_list.append(list(dict_count[i])[1])
					plt.bar(top_actors_list, top_count_list, color=color5, width=0.6)
					pl.xticks(rotation=30, size=8.5)
					for a, b in zip(top_actors_list, top_count_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '10':
					color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
							   'royalblue', 'b', 'darkblue']
					for i in range(10):
						top_actors_list.append(list(dict_count[i])[0])
						top_count_list.append(list(dict_count[i])[1])
					plt.bar(top_actors_list, top_count_list, color=color10, width=0.7)
					pl.xticks(rotation=60, size=8)
					for a, b in zip(top_actors_list, top_count_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('出演次数/次', font2)
			if type == '词云图':
				plt.title(title)
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										# random_state=50,
										stopwords=STOPWORDS)
				if str(top_num) == '3':
					dict_count = dict_count[0:3]
				if str(top_num) == '5':
					dict_count = dict_count[0:5]
				if str(top_num) == '10':
					dict_count = dict_count[0:10]
				plt.imshow(mycloudword.generate_from_frequencies(dict(dict_count)))
				plt.axis("off")
		plt.savefig('draw/' + title + '.jpg', format='jpg')   # 保存图片为 jpg 形式
		plt.close()
	def Top_movie_actors_title(self, type, start_year, end_year, top_num, attribute):
		if attribute != '按出演次数':
			if start_year == end_year:
				title = str(start_year) + "年参演电影" + attribute + "前" + str(top_num) + "的演员" + type
			else:
				title = str(start_year) + '-' + str(end_year) + "年参演电影" + attribute + "前" + str(top_num) + "的演员" + type
		else:
			if start_year == end_year:
				title = str(start_year) + "年出演次数前" + str(top_num) + "的劳模演员" + type
			else:
				title = str(start_year) + '-' + str(end_year) + "年出演次数前" + str(top_num) + "的劳模演员" + type
		return title
	def Top_movie_actors_plot(self):
		plot_title=self.Top_movie_actors_title(self.ids['function'].text,self.search_year_start.text,self.search_year_end.text,self.top_num.text, self.sorting_way.text)
		self.Top_movie_actors(self.ids['function'].text,self.search_year_start.text,self.search_year_end.text,self.top_num.text, self.sorting_way.text)
		self.ids['picture'].source='draw/'+plot_title+'.jpg'
		self.ids['picture'].reload()
		self.current_title=plot_title
	def current_plot_export(self):
		global plots_to_export
		if self.current_title=='':
			NoPlotYet().open()
		else:
			if self.current_title not in plots_to_export:
				plots_to_export.append(self.current_title)
			Exported().open()
	def clear_everything(self):
		self.ids['which_year_start'].text=''
		self.ids['which_year_end'].text=''
		self.ids['which_sorting_way'].text=''
		self.ids['top'].text=''
		self.ids['show_start_year'].state='normal'
		self.ids['show_end_year_selection'].state='normal'
		self.ids['show_sorting_way'].state='normal'
		self.ids['show_top_way'].state='normal'
		self.ids['word cloud'].state='normal'
		self.ids['bar plot'].state='normal'
		self.ids['picture'].source=blank_plot_path
		self.ids['function'].text=''
		self.clear_start_year_selection()
		self.clear_end_year_selection()
		self.clear_sorting_selection()
		self.clear_top_selection()


#top电影界面
class SixthScreen(Screen):
	search_year_start = ObjectProperty()
	search_year_end = ObjectProperty()
	sorting_way = ObjectProperty()
	top_way = ObjectProperty()
	year_text=ObjectProperty()
	end_year=StringProperty()
	months=''
	end_years=[]
	current_title=''
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def show_funtion(self,text):
		self.ids["function"].text=text
	def change_start_year_text(self,text):
		if self.ids['show_start_year'].state == 'down':
			self.search_year_start.text=text
	def change_end_year_text(self,text):
		if self.ids['show_end_year_selection'].state == 'down':
			self.search_year_end.text=text
	def change_sorting_text(self,text):
		if self.ids['show_sorting_way'].state == 'down':
			self.sorting_way.text=text
	def change_top_text(self,text):
		if self.ids['show_top_way'].state == 'down':
			self.top_num.text=text
	def on_end_year(self):
		self.search_year_end.text = text
	def display_selected_end_year(self,text):
		self.search_year_end.text = text
	def show_start_year_selection(self):
		years=["2018","2017","2016","2015"]
		self.year_results_start.item_strings = years
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend(years)
		self.year_results_start._trigger_reset_populate()
	def clear_start_year_selection(self):
		self.year_results_start.item_strings =[]
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend([])
		self.year_results_start._trigger_reset_populate()
	def search_for_end_year(self,start_year):
		self.search_year_end.text=""
		start_end={"2015":["2015","2016","2017","2018"],"2016":["2016","2017","2018"],"2017":["2017","2018"],"2018":["2018"],"":[]}
		self.end_years=start_end[start_year]
		if self.ids['show_end_year_selection'].state == 'down':
			self.show_end_year_selection()
	def show_end_year_selection(self):
		self.year_results_end.item_strings = self.end_years
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend(self.end_years)
		self.year_results_end._trigger_reset_populate()
	def clear_end_year_selection(self):
		self.year_results_end.item_strings =[]
		self.year_results_end.adapter.data.clear()
		self.year_results_end.adapter.data.extend([])
		self.year_results_end._trigger_reset_populate()
	def show_sorting_selection(self):
		selection=["按票房","按评分"]
		self.sorting_selections.item_strings =[selection]
		self.sorting_selections.adapter.data.clear()
		self.sorting_selections.adapter.data.extend(selection)
		self.sorting_selections._trigger_reset_populate()
	def clear_sorting_selection(self):
		self.sorting_selections.item_strings =[]
		self.sorting_selections.adapter.data.clear()
		self.sorting_selections.adapter.data.extend([])
		self.sorting_selections._trigger_reset_populate()
	def show_top_selection(self):
		selection=['3','5','10']
		self.top_selections.item_strings =[selection]
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend(selection)
		self.top_selections._trigger_reset_populate()
	def clear_top_selection(self):
		self.top_selections.item_strings =[]
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend([])
		self.top_selections._trigger_reset_populate()
	def Top_movie_title(self, type, year, top_num, attribute):
		title = str(year) + "年" + attribute + "前" + str(top_num) + "的电影" + type
		return title
	def Top_movie(self, type, year, top_num, attribute):
		data = []
		if str(year) == '2015':
			data = data_2015
		elif str(year) == '2016':
			data = data_2016
		elif str(year) == '2017':
			data = data_2017
		elif str(year) == '2018':
			data = data_2018
		color = ['yellow', 'gold', 'orange', 'navy', 'indigo', 'red', 'blue', 'green', 'm', 'black']
		title = str(year) + "年" + attribute + "前" + str(top_num) + "的电影" + type
		if attribute == '按票房':
			dict_BoxOffice = {}
			for i in range(len(data)):
				if data['film_name'][i] not in dict_BoxOffice.keys():
					dict_BoxOffice[data['film_name'][i]] = int(float(data['box_office'][i]))
			dict_BoxOffice = sorted(dict_BoxOffice.items(), key=lambda d: d[1], reverse=True)
			if type == '条形图':
				top_name_list = []
				top_BoxO_list = []
				if str(top_num) == '3':
					color3 = ['darkorange', 'c', 'limegreen']
					for i in range(3):
						top_name_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_name_list, top_BoxO_list, color=color3, width=0.35)
					for a, b in zip(top_name_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '5':
					color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
					for i in range(5):
						top_name_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_name_list, top_BoxO_list, color=color5, width=0.6)
					pl.xticks(rotation=30, size=8.5)
					for a, b in zip(top_name_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '10':
					color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
							   'royalblue', 'b', 'darkblue']
					for i in range(10):
						top_name_list.append(list(dict_BoxOffice[i])[0])
						top_BoxO_list.append(list(dict_BoxOffice[i])[1])
					plt.bar(top_name_list, top_BoxO_list, color=color10, width=0.7)
					pl.xticks(rotation=60, size=8)
					for a, b in zip(top_name_list, top_BoxO_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('票房/万元', font2)
			if type == '词云图':
				plt.title(title)
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										# random_state=50,
										stopwords=STOPWORDS)
				if str(top_num) == '3':
					dict_BoxOffice = dict_BoxOffice[0:3]
				if str(top_num) == '5':
					dict_BoxOffice = dict_BoxOffice[0:5]
				if str(top_num) == '10':
					dict_BoxOffice = dict_BoxOffice[0:10]
				plt.imshow(mycloudword.generate_from_frequencies(dict(dict_BoxOffice)))
				plt.axis("off")
		if attribute == '按评分':
			dict_score = {}
			for i in range(len(data)):
				if data['film_name'][i] not in dict_score.keys():
					dict_score[data['film_name'][i]] = data['score'][i]
			dict_score = sorted(dict_score.items(), key=lambda d: d[1], reverse=True)
			if type == '条形图':
				top_name_list = []
				top_score_list = []
				if str(top_num) == '3':
					color3 = ['darkorange', 'c', 'limegreen']
					for i in range(3):
						top_name_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_name_list, top_score_list, color=color3, width=0.35)
					for a, b in zip(top_name_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '5':
					color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
					for i in range(5):
						top_name_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_name_list, top_score_list, color=color5, width=0.6)
					pl.xticks(rotation=30, size=8.5)
					for a, b in zip(top_name_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				if str(top_num) == '10':
					color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
							   'royalblue', 'b', 'darkblue']
					for i in range(10):
						top_name_list.append(list(dict_score[i])[0])
						top_score_list.append(list(dict_score[i])[1])
					plt.bar(top_name_list, top_score_list, color=color10, width=0.7)
					pl.xticks(rotation=60, size=8)
					for a, b in zip(top_name_list, top_score_list):
						plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
				plt.title(title, font)
				plt.ylabel('评分/分数', font2)
			if type == '词云图':
				plt.title(title)
				mycloudword = WordCloud(font_path='simkai.ttf',
										width=800,
										height=600,
										scale=6,
										margin=2,
										background_color='white',
										max_words=200,
										min_font_size=20,
										max_font_size=180,
										# random_state=50,
										stopwords=STOPWORDS)
				if str(top_num) == '3':
					dict_score = dict_score[0:3]
				if str(top_num) == '5':
					dict_score = dict_score[0:5]
				if str(top_num) == '10':
					dict_score = dict_score[0:10]
				plt.imshow(mycloudword.generate_from_frequencies(dict(dict_score)))
				plt.axis("off")
		plt.savefig('draw/' + title + '.jpg', format='jpg')
		plt.close()
	def Top_movie_plot(self):
		plot_title=self.Top_movie_title(self.ids['function'].text,self.search_year_start.text,self.top_num.text, self.sorting_way.text)
		self.Top_movie(self.ids['function'].text,self.search_year_start.text,self.top_num.text, self.sorting_way.text)
		self.ids['picture'].source='./draw/'+ plot_title+'.jpg'
		self.ids['picture'].reload()
		self.current_title=plot_title
	def current_plot_export(self):
		global plots_to_export
		if self.current_title=='':
			print("currently no plot")
			NoPlotYet().open()
		else:
			if self.current_title not in plots_to_export:
				plots_to_export.append(self.current_title)
			Exported().open()
	def clear_everything(self):
		self.ids['which_year_start'].text=''
		self.ids['which_sorting_way'].text=''
		self.ids['top'].text=''
		self.ids['show_start_year'].state='normal'
		self.ids['show_sorting_way'].state='normal'
		self.ids['show_top_way'].state='normal'
		self.ids['word cloud'].state='normal'
		self.ids['bar plot'].state='normal'
		self.ids['picture'].source=blank_plot_path
		self.ids['function'].text=''
		self.clear_start_year_selection()
		self.clear_sorting_selection()
		self.clear_top_selection()


# 导出页
class SeventhScreen(Screen):
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def checked(self):
		global plots_to_export_checked
		if len(self.plot_to_export_selection.adapter.selection) == 0:
			NoPlotSelected().open()
			return 0
		else:
			plots_to_export_checked = []
			for i in range(len(self.plot_to_export_selection.adapter.selection)):
				if str(self.plot_to_export_selection.adapter.selection[i])[
				   22:-1] + ".jpg" not in plots_to_export_checked:
					plots_to_export_checked.append(
						str(self.plot_to_export_selection.adapter.selection[i])[22:-1] + ".jpg")
			return 1
	def show_exporting_plots(self):
		self.ids["plot_to_export_selection"].item_strings = plots_to_export
		self.ids["plot_to_export_selection"].adapter.data.clear()
		self.ids["plot_to_export_selection"].adapter.data.extend(plots_to_export)
		self.ids["plot_to_export_selection"]._trigger_reset_populate()
	def clear_everything(self):
		self.ids["plot_to_export_selection"].item_strings = []
		self.ids["plot_to_export_selection"].adapter.data.clear()
		self.ids["plot_to_export_selection"].adapter.data.extend([])
		self.ids["plot_to_export_selection"]._trigger_reset_populate()


class EighthScreen(Screen):
	search_year_start = ObjectProperty()
	top_way = ObjectProperty()
	year_text = ObjectProperty()
	current_title = ''
	def NextPage(self, next):
		if next == 'catalog':
			Window.size = catalog_size
		self.manager.current = next
	def show_funtion(self, text):
		self.ids["function"].text = text
	def change_start_year_text(self, text):
		if self.ids['show_start_year'].state == 'down':
			self.search_year_start.text = text
	def change_top_text(self, text):
		if self.ids['show_top_way'].state == 'down':
			self.top_num.text = text
	def show_start_year_selection(self):
		years = ["2018", "2017", "2016", "2015"]
		self.year_results_start.item_strings = years
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend(years)
		self.year_results_start._trigger_reset_populate()
	def clear_start_year_selection(self):
		self.year_results_start.item_strings = []
		self.year_results_start.adapter.data.clear()
		self.year_results_start.adapter.data.extend([])
		self.year_results_start._trigger_reset_populate()
	def show_top_selection(self):
		selection = ['3', '5', '10']
		self.top_selections.item_strings = [selection]
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend(selection)
		self.top_selections._trigger_reset_populate()
	def clear_top_selection(self):
		self.top_selections.item_strings = []
		self.top_selections.adapter.data.clear()
		self.top_selections.adapter.data.extend([])
		self.top_selections._trigger_reset_populate()
	def Top_movie_director(self, type, year, top_num):
		data = []
		if str(year) == '2015':
			data = data_2015
		elif str(year) == '2016':
			data = data_2016
		elif str(year) == '2017':
			data = data_2017
		elif str(year) == '2018':
			data = data_2018
		dict_BoxOffice = {}
		for i in range(len(data)):
			if data['film_director'][i] not in dict_BoxOffice.keys():
				dict_BoxOffice[data['film_director'][i]] = int(float(data['box_office'][i]))
		dict_BoxOffice = sorted(dict_BoxOffice.items(), key=lambda d: d[1], reverse=True)
		title = str(year) + '年总票房前' + str(top_num) + '的优秀导演' + type
		if type == '条形图':
			top_director_list = []
			top_BoxO_list = []
			if str(top_num) == '3':
				color3 = ['darkorange', 'c', 'limegreen']
				for i in range(3):
					top_director_list.append(list(dict_BoxOffice[i])[0])
					top_BoxO_list.append(list(dict_BoxOffice[i])[1])
				plt.bar(top_director_list, top_BoxO_list, color=color3, width=0.35)
				for a, b in zip(top_director_list, top_BoxO_list):
					plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
			if str(top_num) == '5':
				color5 = ['orangered', 'darkorange', 'gold', 'limegreen', 'royalblue']
				for i in range(5):
					top_director_list.append(list(dict_BoxOffice[i])[0])
					top_BoxO_list.append(list(dict_BoxOffice[i])[1])
				plt.bar(top_director_list, top_BoxO_list, color=color5, width=0.6)
				pl.xticks(rotation=30, size=8.5)
				for a, b in zip(top_director_list, top_BoxO_list):
					plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
			if str(top_num) == '10':
				color10 = ['orangered', 'darkorange', 'gold', 'limegreen', 'mediumspringgreen', 'turquoise', 'c',
						   'royalblue', 'b', 'darkblue']
				for i in range(10):
					top_director_list.append(list(dict_BoxOffice[i])[0])
					top_BoxO_list.append(list(dict_BoxOffice[i])[1])
				plt.bar(top_director_list, top_BoxO_list, color=color10, width=0.7)
				pl.xticks(rotation=60, size=8)
				for a, b in zip(top_director_list, top_BoxO_list):
					plt.text(a, b, b, ha='center', va='bottom', fontsize=9)
			plt.title(title, font)
			plt.ylabel('票房/万元', font2)
		if type == '词云图':
			plt.title(title)
			mycloudword = WordCloud(font_path='simkai.ttf',
									width=800,
									height=600,
									scale=6,
									margin=2,
									background_color='white',
									max_words=200,
									min_font_size=20,
									max_font_size=180,
									# random_state=50,
									stopwords=STOPWORDS)
			if str(top_num) == '3':
				dict_BoxOffice = dict_BoxOffice[0:3]
			if str(top_num) == '5':
				dict_BoxOffice = dict_BoxOffice[0:5]
			if str(top_num) == '10':
				dict_BoxOffice = dict_BoxOffice[0:10]
			plt.imshow(mycloudword.generate_from_frequencies(dict(dict_BoxOffice)))
			plt.axis("off")
		plt.savefig('draw/' + title + '.jpg', format='jpg')
		plt.close()
	def Top_movie_director_title(self, type, year, top_num):
		title = str(year) + '年总票房前' + str(top_num) + '的优秀导演' + type
		return title
	def Top_movie_director_plot(self):
		plot_title = self.Top_movie_director_title(self.ids['function'].text, self.search_year_start.text,
												   self.top_num.text)
		self.Top_movie_director(self.ids['function'].text, self.search_year_start.text, self.top_num.text)
		self.ids['picture'].source = 'draw/' + plot_title + '.jpg'
		self.ids['picture'].reload()
		self.current_title = plot_title
	def current_plot_export(self):
		global plots_to_export
		if self.current_title == '':
			NoPlotYet().open()
		else:
			if self.current_title not in plots_to_export:
				plots_to_export.append(self.current_title)
			Exported().open()
	def clear_everything(self):
		self.ids['which_year_start'].text = ''
		self.ids['top'].text = ''
		self.ids['show_start_year'].state = 'normal'
		self.ids['show_top_way'].state = 'normal'
		self.ids['word cloud'].state = 'normal'
		self.ids['bar plot'].state = 'normal'
		self.ids['picture'].source = blank_plot_path
		self.ids['function'].text = ''
		self.clear_start_year_selection()
		self.clear_top_selection()


# 保存图表页
class SaveDialog(Screen):
	save = ObjectProperty(None)
	text_input = ObjectProperty(None)
	cancel = ObjectProperty(None)
	rootpath = ''
	def __init__(self, **kwargs):
		super(SaveDialog, self).__init__(**kwargs)
		if os.name == 'nt':
			self.rootpath = str(os.getenv('SystemDrive') + '\\USERS\\' + getpass.getuser() + '\\Desktop')  # Windows系统
		else:
			self.rootpath = '/'  	# Unix系统
	def NextPage(self, next_page):
		if next_page == 'seventh':
			Window.size = report_size
		self.manager.current = next_page
	def save(self, path, filename):
		global plots_to_export_checked
		if filename == '':
			NoFileName().open()
		else:
			try:
				convert_images_to_pdf(plots_to_export_checked, path+"/"+filename+".pdf")
				SaveSucceed().open()
			except:
				InvalidPath().open()


class NoPlotSelected(Popup):
	pass
class NoFileName(Popup):
	pass
class InvalidPath(Popup):
	pass
class SaveSucceed(Popup):
	pass
class NoPlotYet(Popup):
	pass
class Exported(Popup):
	pass
class Finished(Popup):
	pass

# listview 打开和按下的button
class MyButton(ToggleButtonBehavior, Image):
	def __init__(self, **kwargs):
		super(MyButton, self).__init__(**kwargs)
		self.source = 'pictures/tg_remove.png'
	def on_state(self, widget, value):
		if value == 'down':
			self.source='pictures/tg_remove_down.png'
		else:
			self.source='pictures/tg_remove.png'


class SearchButton(ToggleButtonBehavior, Image):
	def __init__(self, **kwargs):
		super(SearchButton, self).__init__(**kwargs)
		self.source = 'pictures/search.png'
	def on_state(self, widget, value):
		if value == 'down':
			self.source='pictures/search_down.png'
		else:
			self.source='pictures/search.png'


class SpiderInfo(Popup):
	def update_data(self):
		global years_to_crawl
		update(years_to_crawl)
		self.report_finished(self)
	def start_second_thread(self):
		threading.Thread(target=self.update_data, args=()).start()
	@mainthread
	def report_finished(self, new_text):
		Finished().open()
		read_data()


# 屏幕管理(使用.kv文件的时候生成屏幕管理器)
class MyScreenManager(ScreenManager):
	pass


class SelectionButton(ListItemButton):
	pass


# 生成界面
class MainApp(App):
	def build(self):
		global play_music, have_music
		Window.size = firstpage_size  # 调整窗口大小
		App.title = "星辰电影"
		mixer.init()
		play_music = mixer.music
		play_music.load('./music/'+ str(random.randint(1,7)) + '.mp3')
		play_music.play(loops=-1)
		play_music.set_volume(0.5)
		have_music = True
		return MyScreenManager()


if __name__ == '__main__':
	Factory.register('SaveDialog', cls=SaveDialog)
	read_data()
	idcode.CreateCode((200, 100), 4, (255, 255, 255))
	MainApp().run()
