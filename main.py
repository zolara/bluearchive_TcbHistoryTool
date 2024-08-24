import sys
import os
import platform
import cv2
import datetime
import numpy as np
import csv
import shutil
import configparser
import subprocess
from string import punctuation
from paddleocr import PPStructure
from paddleocr import PaddleOCR, draw_ocrs
import pandas as pd
from jinja2 import Template

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from qt_material import apply_stylesheet


url = os.path.dirname(os.path.abspath(__file__))
os.environ["QT_FONT_DPI"] = "96"

widgets = None

class MainWindow(QWidget):
	signal_setbattlelist = Signal(list,str)
	signal_filename = Signal(str)
    
	def __init__(self):
		super().__init__()
		self.fname = ''
		self.picname = ''
		self.userid =''
		self.cf = configparser.ConfigParser()
		self.cf.read("./conf.ini")
		self.last_filepath = self.cf.get("filepath","last_filepath")
		self.server_la = self.cf.get("server","server_la")
		print(self.last_filepath)
		self.initUI()


	def initUI(self):
		self.resize(1280, 720)  
		self.setWindowTitle('普拉娜的笔记本 v1.2.3')
		#self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMaximizeButtonHint)
		self.setAcceptDrops(True)			
		
		self.btnLoad = QPushButton('查看记录',self)
		self.btnSave = QPushButton('保存记录',self)
		self.btnSearch = QPushButton('查询用户历史阵容',self)
		self.btnAbout = QPushButton('关于',self)
		self.btnRefresh = QPushButton('刷新记录',self)
		self.btnNew = QPushButton('新建记录表',self)
		self.content = QTextEdit()
		self.btnHelp = QPushButton('使用帮助',self)
		self.btnSC = QRadioButton("简体中文（沙勒）")
		self.btnTC = QRadioButton("繁体中文（夏萊）")

		if self.server_la == 'SC':
			self.btnSC.setChecked(True)
		elif self.server_la == 'TC':
			self.btnTC.setChecked(True)
		
		grid = QGridLayout()
		self.setLayout(grid)
		
		TopLayout = QHBoxLayout()
		TopLayout.addStretch(1)
		TopLayout.addWidget(self.btnRefresh)
		
		
		RBLayout = QHBoxLayout()
		RBLayout.addWidget(self.btnSC)
		RBLayout.addWidget(self.btnTC)
		
		grid.addWidget(self.content,1,2,7,2)
		grid.addLayout(TopLayout,8,2,1,2)
		grid.addWidget(self.btnLoad,2,1,1,1)
		grid.addWidget(self.btnSave,3,1,1,1)
		grid.addWidget(self.btnSearch,1,1,1,1)		
		grid.addWidget(self.btnNew,4,1,1,1)
		grid.addLayout(RBLayout,6,1,1,1)
		grid.addWidget(self.btnHelp,7,1,1,1)
		grid.addWidget(self.btnAbout,8,1,1,1)
		
		
		self.btnLoad.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnSave.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnRefresh.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnAbout.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnNew.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnHelp.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.content.setStyleSheet("background-color : rgba(255, 255, 255, 50)")	
		self.btnSC.setIcon(QIcon("QRadioButton::indicator:unchecked {border-image: url(./data/icon/radiobutton_unchecked.svg);}" "QRadioButton::indicator:checked {border-image: url(./source/radiobutton_checked.svg);}"))
		self.btnTC.setIcon(QIcon("QRadioButton::indicator:unchecked {border-image: url(./data/icon/radiobutton_unchecked.svg);}" "QRadioButton::indicator:checked {border-image: url(./source/radiobutton_checked.svg);}"))
		
		self.btnLoad.clicked.connect(self.read_csv)
		self.btnSearch.clicked.connect(self.user_search)
		self.btnSave.clicked.connect(self.add_btnrecord)
		self.btnAbout.clicked.connect(self.show_about)
		self.btnRefresh.clicked.connect(self.refresh_table)
		self.btnNew.clicked.connect(self.new_table)
		self.btnSC.toggled.connect(self.SC_select)
		self.btnTC.toggled.connect(self.TC_select)
		self.btnHelp.clicked.connect(self.show_help)
		
		self.show()
		
	def TC_select(self, event):
		if self.server_la != 'TC':
			self.cf.set('server', 'server_la', 'TC')
			with open('./conf.ini', 'w') as configfile:
				self.cf.write(configfile)
			configfile.close()
		
			print('change to TC')	
			app = QCoreApplication.instance()
			app.quit()
			subprocess.call([sys.executable] + sys.argv)

		
	def SC_select(self, event):
		if self.server_la != 'SC':
			self.cf.set('server', 'server_la', 'SC')
			with open('./conf.ini', 'w') as configfile:
				self.cf.write(configfile)
			configfile.close()
		
			print('change to SC')
			app = QCoreApplication.instance()
			app.quit()
			subprocess.call([sys.executable] + sys.argv)
	
		
	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls:
			if self.fname == '':
				the_dialog = NoCsvOpenDialog()
				if the_dialog.exec() == NoCsvOpenDialog.Accepted:
					pass
			else:
				self.picname = event.mimeData().text()[8:]
				print(event.mimeData().text())
				self.add_newrecord(self)
				event.accept()
		else:
			event.ignore()
			
	def show_help(self, event):
		the_help_dialog = HelpDialog()
		if the_help_dialog.exec() == QDialog.Accepted:
			pass


	def add_newrecord(self, event):
		img_path = self.picname
		file_path = str(self.fname)	
		self.picname = ''
		if self.server_la == 'SC':
			self.ocr_sc(file_path, img_path)
		elif self.server_la == 'TC':
			self.ocr_tc(file_path, img_path)

		
	def add_btnrecord(self, event):
		if self.fname == '':
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			if self.last_filepath == '':
				img_name = QFileDialog.getOpenFileName(self, '选择截图', '.', '*.png')
			else:
				img_name = QFileDialog.getOpenFileName(self, '选择截图', self.last_filepath, '*.png')
				
			img_path = img_name[0]
			file_path = str(self.fname)
			pathMixName = img_path.split('/')
			new_pic_path = "/".join(pathMixName[0:len(pathMixName)-1])
			print(new_pic_path)
			if new_pic_path != '':
				self.last_filepath = new_pic_path
			self.cf.set('filepath', 'last_filepath', new_pic_path)
			with open('./conf.ini', 'w') as configfile:
				self.cf.write(configfile)
			configfile.close()
			
			if self.server_la == 'SC':
				self.ocr_sc(file_path, img_path)
			elif self.server_la == 'TC':
				self.ocr_tc(file_path, img_path)
		
	def ocr_tc(self, file_path, img_path):
		print('record: ' + file_path)
		print('img: ' + img_path)
		if(img_path == ''):
			print("invaild image path!")
		elif(file_path == ''):
			print("invaild csv path!")
		else:		
			table_engine = PPStructure(show_log=False, table=True, image_orientation=False,)
			print("ocr is running.")
						
			img = cv2.imread(img_path)
			cv2.rectangle(img, (1800,790),(1000,870),(216,225,256), -1)
			cv2.rectangle(img, (140,790),(810,870),(246,247,247), -1)
			cv2.rectangle(img, (1480,250),(1560,300),(216,225,256), -1)
			cv2.rectangle(img, (1480,310),(1830,380),(216,225,256), -1)
			
			img1 = img[870:900,1000:1800]
			result1 = table_engine(img1)
			
			try:
				res0 = str(result1[0]['res'][0]['text'])
				new_res0 = ''.join(i for i in res0 if i.isalnum())
			except IndexError: 
				new_res0 = ''
			
			try:
				res1 = str(result1[0]['res'][1]['text'])
				new_res1 = ''.join(i for i in res1 if i.isalnum())
			except IndexError: 
				new_res1 = ''
				
			try:
				res2 = str(result1[0]['res'][2]['text'])
				new_res2 = ''.join(i for i in res2 if i.isalnum())
			except IndexError: 
				new_res2 = ''
			
			try:
				res3 = str(result1[0]['res'][3]['text'])
				new_res3 = ''.join(i for i in res3 if i.isalnum())
			except IndexError: 
				new_res3 = ''
			
			try:
				res4 = str(result1[0]['res'][4]['text'])
				new_res4 = ''.join(i for i in res4 if i.isalnum())
			except IndexError: 
				new_res4 = ''
			
			try:
				res5 = str(result1[0]['res'][5]['text'])
				new_res5 = ''.join(i for i in res5 if i.isalnum())
			except IndexError: 
				new_res5 = ''
			
			print(new_res0 + new_res1 + new_res2 + new_res3 + new_res4 + new_res5)
			
			w_res0 = self.tcocr_to_sc(new_res0)
			w_res1 = self.tcocr_to_sc(new_res1)
			w_res2 = self.tcocr_to_sc(new_res2)
			w_res3 = self.tcocr_to_sc(new_res3)
			w_res4 = self.tcocr_to_sc(new_res4)
			w_res5 = self.tcocr_to_sc(new_res5)
			
			Eatk1 = ''
			Eatk2 = ''
			Eatk3 = ''
			Eatk4 = ''
			Espl1 = ''
			Espl2 = ''
			
			Ecolor2 = img[780,1265].tolist()
			Ecolor3 = img[780,1380].tolist()
			Ecolor4 = img[780,1490].tolist()
			Ecolor5 = img[780,1600].tolist()
						
			if Ecolor2[2]<100:
				Eatk1 = w_res0
				Espl1 = w_res1
				Espl2 = w_res2			
			elif Ecolor3[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Espl1 = w_res2
				Espl2 = w_res3						
			elif Ecolor4[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Espl1 = w_res3
				Espl2 = w_res4						
			elif Ecolor5[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Eatk4 = w_res3
				Espl1 = w_res4
				Espl2 = w_res5
			else:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Eatk4 = w_res3
				Espl1 = w_res4
				Espl2 = w_res5				
			
			img2 = img[230:390,1030:1860]
			result2 = table_engine(img2)

			try:
				res6 = str(result2[0]['res'][0]['text'])
				new_res6 = ''.join(i for i in res6 if i.isalnum())
			except IndexError: 
				new_res6 = ''
			print(new_res6)
			
			try:
				winflag = str(result2[0]['res'][1]['text'])
				new_winflag = ''.join(i for i in winflag if i.isalnum())
			except IndexError: 
				new_winflag = ''
				
			print(new_winflag)
			if new_winflag == 'Win':
				battle_res = "失败"
			else:
				battle_res = "胜利"
			
			img3 = img[870:900,120:820]
			result3 = table_engine(img3)
			
			try:
				my_res0 = str(result3[0]['res'][0]['text'])
				my_new_res0 = ''.join(i for i in my_res0 if i.isalnum())
			except IndexError: 
				my_new_res0 = ''
			
			try:
				my_res1 = str(result3[0]['res'][1]['text'])
				my_new_res1 = ''.join(i for i in my_res1 if i.isalnum())
			except IndexError: 
				my_new_res1 = ''
				
			try:
				my_res2 = str(result3[0]['res'][2]['text'])
				my_new_res2 = ''.join(i for i in my_res2 if i.isalnum())
			except IndexError: 
				my_new_res2 = ''
			
			try:
				my_res3 = str(result3[0]['res'][3]['text'])
				my_new_res3 = ''.join(i for i in my_res3 if i.isalnum())
			except IndexError: 
				my_new_res3 = ''
			
			try:
				my_res4 = str(result3[0]['res'][4]['text'])
				my_new_res4 = ''.join(i for i in my_res4 if i.isalnum())
			except IndexError: 
				my_new_res4 = ''
			
			try:
				my_res5 = str(result3[0]['res'][5]['text'])
				my_new_res5 = ''.join(i for i in my_res5 if i.isalnum())
			except IndexError: 
				my_new_res5 = ''
			
			print(my_new_res0 + my_new_res1 + my_new_res2 + my_new_res3 + my_new_res4 + my_new_res5)
			
			my_w_res0 = self.tcocr_to_sc(my_new_res0)
			my_w_res1 = self.tcocr_to_sc(my_new_res1)
			my_w_res2 = self.tcocr_to_sc(my_new_res2)
			my_w_res3 = self.tcocr_to_sc(my_new_res3)
			my_w_res4 = self.tcocr_to_sc(my_new_res4)
			my_w_res5 = self.tcocr_to_sc(my_new_res5)
			
			Fatk1 = ''
			Fatk2 = ''
			Fatk3 = ''
			Fatk4 = ''
			Fspl1 = ''
			Fspl2 = ''
			
			Fcolor2 = img[780,310].tolist()
			Fcolor3 = img[780,420].tolist()
			Fcolor4 = img[780,535].tolist()
			Fcolor5 = img[780,650].tolist()

			if Fcolor2[2]<100:
				Fatk1 = my_w_res0
				Fspl1 = my_w_res1
				Fspl2 = my_w_res2			
			elif Fcolor3[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fspl1 = my_w_res2
				Fspl2 = my_w_res3						
			elif Fcolor4[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fspl1 = my_w_res3
				Fspl2 = my_w_res4						
			elif Fcolor5[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fatk4 = my_w_res3
				Fspl1 = my_w_res4
				Fspl2 = my_w_res5
			else:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fatk4 = my_w_res3
				Fspl1 = my_w_res4
				Fspl2 = my_w_res5	
			
			
			pixel_value_format = img[340,100].tolist()
			print(pixel_value_format)
			if pixel_value_format == [131,98,61]:
				format = "进攻"
			elif pixel_value_format[0]>120 and pixel_value_format[0]<140 and pixel_value_format[1]>90 and pixel_value_format[1]<110 and pixel_value_format[2]>50 and pixel_value_format[2]<70:
				format = "进攻"
			else:
				format = "防守"
			print(format)
			
			
			print(battle_res)		
						
			battle_list = [new_res6, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, battle_res, format]
			print(battle_list)
			confirm_dialog = ConfirmDialog()
			self.signal_setbattlelist.emit(battle_list,file_path)
			if confirm_dialog.exec() == QDialog.Accepted:
				pass
			
	def ocr_sc(self, file_path, img_path):
		print('record: ' + file_path)
		print('img: ' + img_path)
		if(img_path == ''):
			print("invaild image path!")
		elif(file_path == ''):
			print("invaild csv path!")
		else:		
			table_engine = PPStructure(show_log=False, table=True, image_orientation=False,)
			print("ocr is running.")
						
			img = cv2.imread(img_path)
			cv2.rectangle(img, (1800,790),(1000,870),(216,225,256), -1)
			cv2.rectangle(img, (140,790),(810,870),(246,247,247), -1)

			
			img1 = img[870:900,1000:1800]
			result1 = table_engine(img1)
			
			try:
				res0 = str(result1[0]['res'][0]['text'])
				new_res0 = ''.join(i for i in res0 if i.isalnum())
			except IndexError: 
				new_res0 = ''
			
			try:
				res1 = str(result1[0]['res'][1]['text'])
				new_res1 = ''.join(i for i in res1 if i.isalnum())
			except IndexError: 
				new_res1 = ''
				
			try:
				res2 = str(result1[0]['res'][2]['text'])
				new_res2 = ''.join(i for i in res2 if i.isalnum())
			except IndexError: 
				new_res2 = ''
			
			try:
				res3 = str(result1[0]['res'][3]['text'])
				new_res3 = ''.join(i for i in res3 if i.isalnum())
			except IndexError: 
				new_res3 = ''
			
			try:
				res4 = str(result1[0]['res'][4]['text'])
				new_res4 = ''.join(i for i in res4 if i.isalnum())
			except IndexError: 
				new_res4 = ''
			
			try:
				res5 = str(result1[0]['res'][5]['text'])
				new_res5 = ''.join(i for i in res5 if i.isalnum())
			except IndexError: 
				new_res5 = ''
			
			w_res0 = self.scocr_to_sc(new_res0)
			w_res1 = self.scocr_to_sc(new_res1)
			w_res2 = self.scocr_to_sc(new_res2)
			w_res3 = self.scocr_to_sc(new_res3)
			w_res4 = self.scocr_to_sc(new_res4)
			w_res5 = self.scocr_to_sc(new_res5)
			
			Eatk1 = ''
			Eatk2 = ''
			Eatk3 = ''
			Eatk4 = ''
			Espl1 = ''
			Espl2 = ''
			
			Ecolor2 = img[780,1265].tolist()
			Ecolor3 = img[780,1380].tolist()
			Ecolor4 = img[780,1490].tolist()
			Ecolor5 = img[780,1600].tolist()
						
			if Ecolor2[2]<100:
				Eatk1 = w_res0
				Espl1 = w_res1
				Espl2 = w_res2			
			elif Ecolor2[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Espl1 = w_res2
				Espl2 = w_res3						
			elif Ecolor2[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Espl1 = w_res3
				Espl2 = w_res4						
			elif Ecolor2[2]<100:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Eatk4 = w_res3
				Espl1 = w_res4
				Espl2 = w_res5
			else:
				Eatk1 = w_res0
				Eatk2 = w_res1
				Eatk3 = w_res2
				Eatk4 = w_res3
				Espl1 = w_res4
				Espl2 = w_res5				
			
			print(new_res0 + new_res1 + new_res2 + new_res3 + new_res4 + new_res5)
			
			img2 = img[250:370,1290:1860]
			result2 = table_engine(img2)

			try:
				res6 = str(result2[0]['res'][1]['text'])
				new_res6 = ''.join(i for i in res6 if i.isalnum())
			except IndexError: 
				new_res6 = ''
			print(new_res6)
			
			
			img3 = img[870:900,120:820]
			result3 = table_engine(img3)
			
			try:
				my_res0 = str(result3[0]['res'][0]['text'])
				my_new_res0 = ''.join(i for i in my_res0 if i.isalnum())
			except IndexError: 
				my_new_res0 = ''
			
			try:
				my_res1 = str(result3[0]['res'][1]['text'])
				my_new_res1 = ''.join(i for i in my_res1 if i.isalnum())
			except IndexError: 
				my_new_res1 = ''
				
			try:
				my_res2 = str(result3[0]['res'][2]['text'])
				my_new_res2 = ''.join(i for i in my_res2 if i.isalnum())
			except IndexError: 
				my_new_res2 = ''
			
			try:
				my_res3 = str(result3[0]['res'][3]['text'])
				my_new_res3 = ''.join(i for i in my_res3 if i.isalnum())
			except IndexError: 
				my_new_res3 = ''
			
			try:
				my_res4 = str(result3[0]['res'][4]['text'])
				my_new_res4 = ''.join(i for i in my_res4 if i.isalnum())
			except IndexError: 
				my_new_res4 = ''
			
			try:
				my_res5 = str(result3[0]['res'][5]['text'])
				my_new_res5 = ''.join(i for i in my_res5 if i.isalnum())
			except IndexError: 
				my_new_res5 = ''
			
			print(my_new_res0 + my_new_res1 + my_new_res2 + my_new_res3 + my_new_res4 + my_new_res5)
			
			my_w_res0 = self.scocr_to_sc(my_new_res0)
			my_w_res1 = self.scocr_to_sc(my_new_res1)
			my_w_res2 = self.scocr_to_sc(my_new_res2)
			my_w_res3 = self.scocr_to_sc(my_new_res3)
			my_w_res4 = self.scocr_to_sc(my_new_res4)
			my_w_res5 = self.scocr_to_sc(my_new_res5)
			
			Fatk1 = ''
			Fatk2 = ''
			Fatk3 = ''
			Fatk4 = ''
			Fspl1 = ''
			Fspl2 = ''
			
			Fcolor2 = img[780,310].tolist()
			Fcolor3 = img[780,420].tolist()
			Fcolor4 = img[780,535].tolist()
			Fcolor5 = img[780,650].tolist()
					
			if Fcolor2[2]<100:
				Fatk1 = my_w_res0
				Fspl1 = my_w_res1
				Fspl2 = my_w_res2			
			elif Fcolor3[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fspl1 = my_w_res2
				Fspl2 = my_w_res3						
			elif Fcolor4[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fspl1 = my_w_res3
				Fspl2 = my_w_res4						
			elif Fcolor5[2]<100:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fatk4 = my_w_res3
				Fspl1 = my_w_res4
				Fspl2 = my_w_res5
			else:
				Fatk1 = my_w_res0
				Fatk2 = my_w_res1
				Fatk3 = my_w_res2
				Fatk4 = my_w_res3
				Fspl1 = my_w_res4
				Fspl2 = my_w_res5
			
			pixel_value = img[300,230].tolist()
			if pixel_value == [227,229,234]:
				battle_res = "失败"
			elif pixel_value[0]>220 and pixel_value[0]<235 and pixel_value[1]>225 and pixel_value[1]<235 and pixel_value[2]>230 and pixel_value[2]<240:
				battle_res = "失败"
			else:
				battle_res = "胜利"
			print(battle_res)	

			pixel_value_format = img[340,100].tolist()
			if pixel_value_format == [128,94,56]:
				format = "进攻"
			elif pixel_value_format[0]>120 and pixel_value_format[0]<140 and pixel_value_format[1]>85 and pixel_value_format[1]<105 and pixel_value_format[2]>45 and pixel_value_format[2]<65:
				format = "进攻"
			else:
				format = "防守"
			print(format)
						
			battle_list = [new_res6, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, battle_res, format]
			
			confirm_dialog = ConfirmDialog()
			self.signal_setbattlelist.emit(battle_list,file_path)
			if confirm_dialog.exec() == QDialog.Accepted:
				pass
			
	def show_csv(self, df_img):	
		df_length = len(df_img)
		for num in range(0,df_length):
			template_string_data = '''
			<table border="1" align="center" style="background-color: rgba(255, 255, 255, 0.5);" >
				<tr>
					<th colspan="9">{{ UserId }}</th>
				</tr>
				<tr>
					<th>{{ FAttacker1 }}</th>
					<th>{{ FAttacker2 }}</th>
					<th>{{ FAttacker3 }}</th>
					<th>{{ FAttacker4 }}</th>
					<th>{{ Result }}</th>
					<th>{{ EAttacker1 }}</th>
					<th>{{ EAttacker2 }}</th>
					<th>{{ EAttacker3 }}</th>
					<th>{{ EAttacker4 }}</th>
				</tr>
				<tr>
					<th>{{ Date }}</th>
					<th>{{ space }}</th>
					<th>{{ FSpecial1 }}</th>
					<th>{{ FSpecial2 }}</th>
					<th>{{ Formation }}</th>
					<th>{{ space }}</th>
					<th>{{ space }}</th>
					<th>{{ ESpecial1 }}</th>
					<th>{{ ESpecial2 }}</th>
				</tr>
			'''

			template_data = Template(template_string_data)
			html_data = template_data.render(
				UserId = '<br><br>' + str(df_img.iloc[num,0]),
				Date = '<br><br>' + str(df_img.iloc[num,1]),				
				FAttacker1 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,2] + '.png width=80/>',
				FAttacker2 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,3] + '.png width=80/>',
				FAttacker3 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,4] + '.png width=80/>',
				FAttacker4 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,5] + '.png width=80/>',
				FSpecial1 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,6] + '.png width=80/>',
				FSpecial2 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,7] + '.png width=80/>',
				Formation = '<br><img src=' + url + '/data/images/' + df_img.iloc[num,8] + '.png width=80/>',
				EAttacker1 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,9] + '.png width=80/>',
				EAttacker2 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,10] + '.png width=80/>',
				EAttacker3 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,11] + '.png width=80/>',
				EAttacker4 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,12] + '.png width=80/>',
				ESpecial1 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,13] + '.png width=80/>',
				ESpecial2 = '<img src=' + url + '/data/images/stud/' + df_img.iloc[num,14] + '.png width=80/>',
				Result = '<br><img src=' + url + '/data/images/' + df_img.iloc[num,15] + '.png width=80/>',
				Me = '<br><br>' + '我的阵容',
				space = ''
			)
			self.content.append(html_data)
			self.content.append('\n\n')
			
	def read_csv(self, event):
		fname_r, fpath= QFileDialog.getOpenFileName(self, '选择csv记录', './table', '*.csv')
		if fname_r == '' :
			print(self.fname)
			pass
		else:
			self.fname = fname_r

			print(self.fname)
			df = pd.read_csv(self.fname)	
			self.content.clear()
			df_img = df.tail(50)
			self.show_csv(df_img)
			
	def refresh_table(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			print(self.fname)
			df = pd.read_csv(self.fname)	
			self.content.clear()
			df_img = df.tail(50)
			self.show_csv(df_img)
				
	def show_about(self):
		about_dialog = AboutDialog()
		if about_dialog.exec() == QDialog.Accepted:
			pass
		
	def user_search(self):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			search_dialog = SearchDialog()
			search_dialog.signal_setid.connect(self.get_id)
			file_path = str(self.fname)
			self.signal_filename.emit(file_path)
			if search_dialog.exec() == QDialog.Accepted:
				pass
			

	def new_table(self):
		new_dialog = NewCsvDialog()
		if new_dialog.exec() == QDialog.Accepted:
			pass					

	def paintEvent(self, event):		
		painter = QPainter(self)
		if self.server_la == 'SC':
			pixmap = QPixmap("./data/images/bg.png")
		elif self.server_la == 'TC':
			pixmap = QPixmap("./data/images/bg_tc.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	def get_id(self,userid):
		self.userid = userid
		print('get ' + self.userid)
		self.content.clear()
		self.content.append(userid)
		
		df = pd.read_csv(self.fname)	
		df_img = df[df['UserId'] == userid]
		print(df_img)
		self.show_csv(df_img)
			
	def sc_to_code(self,stud):
		stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
		return stud_dict[stud]
		
	def scocr_to_sc(self,stud):
		stud_dict = pd.read_json('./data/studstr_scocr2sc.json', typ='series')
		try:
			stud_name = stud_dict[stud]
		except KeyError:
			stud_name = ''
		return stud_name
		
	def tcocr_to_sc(self,stud):
		stud_dict = pd.read_json('./data/studstr_tcocr2sc.json', typ='series')
		try:
			stud_name = stud_dict[stud]
		except KeyError:
			stud_name = ''
		return stud_name
		
class HelpDialog(QDialog):
		def __init__(self):
			super().__init__()
			self.initUI()

		def initUI(self):
			self.setWindowTitle('使用帮助')
			self.setFixedSize(600, 300) 
			self.content = QTextEdit()
			self.content.verticalScrollBar().setValue(self.content.verticalScrollBar().maximum())

			self.buttonclose = QPushButton('OK',self)
			self.buttonclose.clicked.connect(self.close)

			grid = QGridLayout()
			grid.addWidget(self.content,1,1,1,2)
			grid.addWidget(self.buttonclose,2,2,1,1)
			self.setLayout(grid)
		
			txtfile = QFile("./data/help.txt")
			if not txtfile.open(QFile.ReadOnly | QFile.Text):
				return -1
			stream = QTextStream(txtfile)
			text = stream.readAll()
			self.content.setHtml("<font size='5' ><b>" + text + "</b></font>")
			self.setWindowFlags(Qt.FramelessWindowHint)
			self.setWindowOpacity(0.8)

class ConfirmDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.file_name = ''
		window.signal_setbattlelist.connect(self.get_battlelist)
		
		
	def initUI(self):
		self.setFixedSize(600, 540)  
		self.setWindowTitle('确认数据')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
		stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
		completer_words = list(stud_dict.keys())
		completer = QCompleter(completer_words)
		
		self.btnOk = QPushButton('OK',self)

		self.label_f1 = QLabel('我方突击①', self)
		self.label_f2 = QLabel('我方突击②', self)
		self.label_f3 = QLabel('我方突击③', self)
		self.label_f4 = QLabel('我方突击④', self)
		self.label_f5 = QLabel('我方支援①', self)
		self.label_f6 = QLabel('我方支援②', self)
		self.label_e1 = QLabel('敌方突击①', self)
		self.label_e2 = QLabel('敌方突击②', self)
		self.label_e3 = QLabel('敌方突击③', self)
		self.label_e4 = QLabel('敌方突击④', self)
		self.label_e5 = QLabel('敌方支援①', self)
		self.label_e6 = QLabel('敌方支援②', self)
		self.label_user = QLabel('对手ID', self)	
		self.label_res = QLabel('对战结果', self)
		self.label_format = QLabel('编队模式', self)
		
		self.lineEdit_f1 = QLineEdit()
		self.lineEdit_f2 = QLineEdit()
		self.lineEdit_f3 = QLineEdit()
		self.lineEdit_f4 = QLineEdit()
		self.lineEdit_f5 = QLineEdit()
		self.lineEdit_f6 = QLineEdit()
		self.lineEdit_e1 = QLineEdit()
		self.lineEdit_e2 = QLineEdit()
		self.lineEdit_e3 = QLineEdit()
		self.lineEdit_e4 = QLineEdit()
		self.lineEdit_e5 = QLineEdit()
		self.lineEdit_e6 = QLineEdit()
		self.lineEdit_user = QLineEdit()
		self.ComboBox_res = QComboBox()
		self.ComboBox_format = QComboBox()
		
		self.lineEdit_f1.setCompleter(completer)
		self.lineEdit_f2.setCompleter(completer)
		self.lineEdit_f3.setCompleter(completer)
		self.lineEdit_f4.setCompleter(completer)
		self.lineEdit_f5.setCompleter(completer)
		self.lineEdit_f6.setCompleter(completer)
		self.lineEdit_e1.setCompleter(completer)
		self.lineEdit_e2.setCompleter(completer)
		self.lineEdit_e3.setCompleter(completer)
		self.lineEdit_e4.setCompleter(completer)
		self.lineEdit_e5.setCompleter(completer)
		self.lineEdit_e6.setCompleter(completer)
		
		self.ComboBox_res.setEditable(True)
		self.ComboBox_res.addItems(["胜利", "失败"])
		self.ComboBox_res.setStyleSheet("QComboBox::down-arrow {image: url(./data/icon/down_arrow.svg);}")
		self.ComboBox_format.setEditable(True)
		self.ComboBox_format.addItems(["进攻", "防守"])
		self.ComboBox_format.setStyleSheet("QComboBox::down-arrow {image: url(./data/icon/down_arrow.svg);}")
	
		grid = QGridLayout()
		self.setLayout(grid)
		
		grid.addWidget(self.label_f1,1,1,1,1)
		grid.addWidget(self.label_f2,1,2,1,1)
		grid.addWidget(self.label_f3,1,3,1,1)
		grid.addWidget(self.label_f4,1,4,1,1)
		grid.addWidget(self.lineEdit_f1,2,1,1,1)
		grid.addWidget(self.lineEdit_f2,2,2,1,1)
		grid.addWidget(self.lineEdit_f3,2,3,1,1)
		grid.addWidget(self.lineEdit_f4,2,4,1,1)
		
		grid.addWidget(self.label_f5,3,3,1,1)
		grid.addWidget(self.label_f6,3,4,1,1)
		grid.addWidget(self.lineEdit_f5,4,3,1,1)
		grid.addWidget(self.lineEdit_f6,4,4,1,1)
		
		grid.addWidget(self.label_e1,5,1,1,1)
		grid.addWidget(self.label_e2,5,2,1,1)
		grid.addWidget(self.label_e3,5,3,1,1)
		grid.addWidget(self.label_e4,5,4,1,1)
		grid.addWidget(self.lineEdit_e1,6,1,1,1)
		grid.addWidget(self.lineEdit_e2,6,2,1,1)
		grid.addWidget(self.lineEdit_e3,6,3,1,1)
		grid.addWidget(self.lineEdit_e4,6,4,1,1)
		
		grid.addWidget(self.label_e5,7,3,1,1)
		grid.addWidget(self.label_e6,7,4,1,1)
		grid.addWidget(self.lineEdit_e5,8,3,1,1)
		grid.addWidget(self.lineEdit_e6,8,4,1,1)
		
		grid.addWidget(self.label_user,9,3,1,1)
		grid.addWidget(self.label_res,9,4,1,1)
		grid.addWidget(self.lineEdit_user,10,3,1,1)
		grid.addWidget(self.ComboBox_res,10,4,1,1)
		
		grid.addWidget(self.label_format,11,4,1,1)
		grid.addWidget(self.ComboBox_format,12,4,1,1)
		
		grid.addWidget(self.btnOk,13,4,1,1)

		self.label_f1.setAlignment(Qt.AlignCenter)
		self.label_f2.setAlignment(Qt.AlignCenter)
		self.label_f3.setAlignment(Qt.AlignCenter)
		self.label_f4.setAlignment(Qt.AlignCenter)
		self.label_f5.setAlignment(Qt.AlignCenter)
		self.label_f6.setAlignment(Qt.AlignCenter)
		self.label_e1.setAlignment(Qt.AlignCenter)
		self.label_e2.setAlignment(Qt.AlignCenter)
		self.label_e3.setAlignment(Qt.AlignCenter)
		self.label_e4.setAlignment(Qt.AlignCenter)
		self.label_e5.setAlignment(Qt.AlignCenter)
		self.label_e6.setAlignment(Qt.AlignCenter)
		self.label_user.setAlignment(Qt.AlignCenter)
		self.label_res.setAlignment(Qt.AlignCenter)
		self.label_format.setAlignment(Qt.AlignCenter)
		
		self.label_f1.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_f2.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_f3.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_f4.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_f5.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_f6.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e1.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e2.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e3.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e4.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e5.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_e6.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_user.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_res.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_format.setStyleSheet("font-weight:bold;font-size:16px")
				
		self.btnOk.setStyleSheet("background-color : rgba(176,196,222,1)")
		
		self.btnOk.clicked.connect(self.insert_table)
		self.btnOk.clicked.connect(self.close)
		
		self.show()
		
	def get_battlelist(self, battle_list, file_name):
		self.lineEdit_user.setText(battle_list[0])
		self.lineEdit_e1.setText(battle_list[1])
		self.lineEdit_e2.setText(battle_list[2])
		self.lineEdit_e3.setText(battle_list[3])
		self.lineEdit_e4.setText(battle_list[4])
		self.lineEdit_e5.setText(battle_list[5])
		self.lineEdit_e6.setText(battle_list[6])
		self.lineEdit_f1.setText(battle_list[7])
		self.lineEdit_f2.setText(battle_list[8])
		self.lineEdit_f3.setText(battle_list[9])
		self.lineEdit_f4.setText(battle_list[10])
		self.lineEdit_f5.setText(battle_list[11])
		self.lineEdit_f6.setText(battle_list[12])
		self.ComboBox_res.setCurrentText(battle_list[13])
		self.ComboBox_format.setCurrentText(battle_list[14])
		self.file_path = file_name
		
	def sc_to_code(self,stud):
		if stud != '':
			stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
			return stud_dict[stud]
		else:
			return '1NoData'
		
	def scocr_to_sc(self,stud):
		stud_dict = pd.read_json('./data/studstr_scocr2sc.json', typ='series')
		try:
			stud_name = stud_dict[stud]
		except KeyError:
			stud_name = ''
		return stud_name
		
	def insert_table(self, event):
		print('insert: ')
		
		userId = self.lineEdit_user.text()
		result = self.ComboBox_res.currentText()
		Fatk1 = self.sc_to_code(self.lineEdit_f1.text())
		Fatk2 = self.sc_to_code(self.lineEdit_f2.text())
		Fatk3 = self.sc_to_code(self.lineEdit_f3.text())
		Fatk4 = self.sc_to_code(self.lineEdit_f4.text())
		Fspl1 = self.sc_to_code(self.lineEdit_f5.text())
		Fspl2 = self.sc_to_code(self.lineEdit_f6.text())
		Eatk1 = self.sc_to_code(self.lineEdit_e1.text())
		Eatk2 = self.sc_to_code(self.lineEdit_e2.text())
		Eatk3 = self.sc_to_code(self.lineEdit_e3.text())
		Eatk4 = self.sc_to_code(self.lineEdit_e4.text())
		Espl1 = self.sc_to_code(self.lineEdit_e5.text())
		Espl2 = self.sc_to_code(self.lineEdit_e6.text())
		formation = self.ComboBox_format.currentText()
		
		with open(self.file_path, "a", encoding="utf-8", newline="") as f:
			wf = csv.writer(f)
			new_data = [userId,str(datetime.date.today()),Fatk1,Fatk2,Fatk3,Fatk4,Fspl1,Fspl2,formation,Eatk1,Eatk2,Eatk3,Eatk4,Espl1,Espl2,result]
			wf.writerow(new_data)
			f.close()
	

	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/confirm.png")
		painter.drawPixmap(self.rect(), pixmap)

		
			
class SearchDialog(QDialog):
	signal_setid = Signal(str)
	
	def __init__(self):
		super().__init__()
		self.initUI()
		window.signal_filename.connect(self.get_file_name)
		
		
	def initUI(self):
		self.setFixedSize(400, 400)  
		self.setWindowTitle('查询用户历史阵容')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		
		self.label = QLabel('请输入用户ID', self)
		self.lineEdit = QLineEdit(self)
		self.btnOk = QPushButton('查询',self)
		
		self.btnOk.clicked.connect(self.set_userid)
		self.btnOk.clicked.connect(self.close)	
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label)
		vbox.addWidget(self.lineEdit)
		vbox.addWidget(self.btnOk)
		vbox.addStretch(1)
		self.setLayout(vbox)
		self.show()
		
	def get_file_name(self, file_path):
		df = pd.read_csv(file_path)
		user_list = list(set(df['UserId']))
		completer = QCompleter(user_list)
		completer.setFilterMode(Qt.MatchContains)
		self.lineEdit.setCompleter(completer)
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/search.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	def set_userid(self):
		userid = self.lineEdit.text()
		self.signal_setid.emit(userid)
		
class NewCsvDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()
		
		
	def initUI(self):
		self.setFixedSize(400, 400)  
		self.setWindowTitle('新建一张记录表')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		
		self.label = QLabel('请输入文件名（不带.csv）', self)
		self.lineEdit = QLineEdit(self)
		self.btnOk = QPushButton('OK',self)
		
		self.btnOk.clicked.connect(self.new_cvs)
		self.btnOk.clicked.connect(self.close)		
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label)
		vbox.addWidget(self.lineEdit)
		vbox.addWidget(self.btnOk)
		vbox.addStretch(1)
		self.setLayout(vbox)
		self.show()
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/search.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	def new_cvs(self):
		file_name = self.lineEdit.text()
		src_file = './data/templates/tcb_template.csv'
		dst_folder = './table/' + file_name + '.csv'
		
		if os.path.exists('./table/'  + file_name + '.csv'):
			print('file Duplicate! Please change a file name.')
		else:
			shutil.copy(src_file, dst_folder)
					
		
		
class NoCsvOpenDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('没有被打开的记录文件')
		self.setFixedSize(400, 400)
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		
		
		self.label1 = QLabel()
		self.label1.setText("请先打开一张记录表")
		self.label1.setAlignment(Qt.AlignCenter)
		self.label1.setStyleSheet("font-weight:bold;font-size:20px;color:rgb(100,149,237)")
		
		self.buttonclose = QPushButton('OK',self)
		self.buttonclose.clicked.connect(self.close)
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label1)
		vbox.addStretch(1)
		vbox.addWidget(self.buttonclose)
		self.setLayout(vbox)
		self.show()
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/Nocsv.png")
		painter.drawPixmap(self.rect(), pixmap)
		
    
class AboutDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('关于')
		self.setFixedSize(550, 200)
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)

		self.label1 = QLabel()
		self.label1.setText("本软件遵循GPL开源协议\n开发作者：苦艾煎茶")
		self.label1.setAlignment(Qt.AlignLeft)
		self.label1.setStyleSheet("font-weight:bold;font-size:20px")
		
		self.label3 = QLabel()
		self.label3.setText('<a href="https://space.bilibili.com/347996989">B站ID：Hamism</a>')
		self.label3.setAlignment(Qt.AlignLeft)
		self.label3.setOpenExternalLinks(True)
		self.label3.setStyleSheet("font-weight:bold;font-size:20px;color:black")
		
		self.label4 = QLabel()
		self.label4.setText('<a href="https://github.com/zolara/bluearchive_TcbHistoryTool">Github：bluearchive_TcbHistoryTool</a>')
		self.label4.setAlignment(Qt.AlignLeft)
		self.label4.setOpenExternalLinks(True)
		self.label4.setStyleSheet("font-weight:bold;font-size:20px;color:black")
		
		self.label5 = QLabel()
		self.label5.setFixedSize(20, 20)
		self.label5.setAlignment(Qt.AlignRight)
		pixmap = QPixmap("./data/images/bilibili.png")
		self.label5.setScaledContents(True)
		self.label5.setPixmap(pixmap)
		
		self.label6 = QLabel()
		self.label6.setFixedSize(20, 20)
		self.label6.setAlignment(Qt.AlignRight)
		pixmap = QPixmap("./data/images/github.png")
		self.label6.setScaledContents(True)
		self.label6.setPixmap(pixmap)
		
		self.btnOk = QPushButton('OK',self)
		self.btnOk.clicked.connect(self.close)

		grid = QGridLayout()
		self.setLayout(grid)
		grid.setAlignment(Qt.AlignRight)
		grid.addWidget(self.label1,1,3,1,1)
		grid.addWidget(self.label3,3,3,1,1)
		grid.addWidget(self.label4,4,3,1,1)
		grid.addWidget(self.label5,3,2,1,1)
		grid.addWidget(self.label6,4,2,1,1)	
		grid.addWidget(self.btnOk,5,3,1,1)		

		self.setWindowOpacity(0.8)
		self.show()
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/About.png")
		painter.drawPixmap(self.rect(), pixmap)

	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	apply_stylesheet(app, theme= url+'/qt_material/themes/light_cyan_501.xml') 
	app.setWindowIcon(QIcon(url+"/data/images/icon.ico"))
	app.setAttribute(Qt.AA_UseHighDpiPixmaps)
	window = MainWindow()
	sys.exit(app.exec())