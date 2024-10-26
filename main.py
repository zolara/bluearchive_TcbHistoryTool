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
import requests
from string import punctuation
from paddleocr import PPStructure
from paddleocr import PaddleOCR, draw_ocr
import pandas as pd
from jinja2 import Template
from tkinter import *
from tkinter import filedialog, messagebox

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from qt_material import apply_stylesheet


url = os.path.dirname(os.path.abspath(__file__))
web_url = 'http://124.223.5.69:8181'
os.environ["QT_FONT_DPI"] = "96"

widgets = None

class MainWindow(QWidget):
	signal_setbattlelist = Signal(list,str,str)
	signal_filename = Signal(str)
	signal_bulklog = Signal(list)
    
	def __init__(self):
		super().__init__()
		self.fname = ''
		self.picname = ''
		self.userid = ''
		self.df_output = pd.DataFrame()
		self.cf = configparser.ConfigParser()
		self.cf.read("./conf.ini")
		self.last_filepath = self.cf.get("filepath","last_filepath")
		self.server_la = self.cf.get("server","server_la")
		print(self.last_filepath)
		self.initUI()

	def initUI(self):
		self.resize(1280, 720)  
		self.setWindowTitle('普拉娜的笔记本 v1.4.1')
		#self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMaximizeButtonHint)
		self.setAcceptDrops(True)			
		
		self.btnLoad = QPushButton('查看记录',self)
		self.btnSave = QPushButton('保存记录',self)
		self.btnMSave = QPushButton('手动保存记录',self)
		self.btnBulkSave = QPushButton('批量保存记录',self)
		self.btnSearch = QPushButton('查询用户历史阵容',self)
		self.btnAbout = QPushButton('关于',self)
		self.btnRefresh = QPushButton('刷新记录',self)
		self.btnReplaceid = QPushButton('替换用户ID',self)
		self.btnDelete = QPushButton('修改记录项',self)
		self.btnOutput = QPushButton('导出为新记录表',self)
		self.btnNew = QPushButton('新建记录表',self)
		self.btnData = QPushButton('模糊查询',self)
		self.btnQuery = QPushButton('精确查询',self)
		self.btnUpload = QPushButton('上传到网站',self)
		self.content = QTextBrowser()
		self.btnHelp = QPushButton('使用帮助',self)
		self.btnSC = QRadioButton("简体中文")
		self.btnTC = QRadioButton("繁体中文")
		self.btnJP = QRadioButton("日文")
		
		self.content.setReadOnly(True)
		self.content.setOpenLinks(True)
		self.content.setOpenExternalLinks(True)

		if self.server_la == 'SC':
			self.btnSC.setChecked(True)
		elif self.server_la == 'TC':
			self.btnTC.setChecked(True)
		elif self.server_la == 'JP':
			self.btnJP.setChecked(True)
		
		grid = QGridLayout()
		self.setLayout(grid)
		
		TopLayout = QHBoxLayout()
		TopLayout.addStretch(1)
		TopLayout.addWidget(self.btnOutput)
		TopLayout.addWidget(self.btnDelete)
		TopLayout.addWidget(self.btnReplaceid)
		TopLayout.addWidget(self.btnRefresh)
		
		MidLayout = QHBoxLayout()
		MidLayout.addWidget(self.btnQuery)
		MidLayout.addWidget(self.btnData)
		
		MidLayout1 = QHBoxLayout()
		MidLayout1.addWidget(self.btnMSave)
		MidLayout1.addWidget(self.btnBulkSave)
	
		RBLayout = QHBoxLayout()
		RBLayout.addWidget(self.btnSC)
		RBLayout.addWidget(self.btnTC)
		RBLayout.addWidget(self.btnJP)
		
		grid.addWidget(self.content,1,2,10,2)
		grid.addLayout(TopLayout,11,2,1,2)
		grid.addWidget(self.btnLoad,2,1,1,1)
		grid.addWidget(self.btnSave,3,1,1,1)
		grid.addLayout(MidLayout1,4,1,1,1)
		grid.addWidget(self.btnSearch,1,1,1,1)		
		grid.addWidget(self.btnNew,5,1,1,1)
		grid.addLayout(MidLayout,6,1,1,1)
		grid.addWidget(self.btnUpload,7,1,1,1)
		grid.addLayout(RBLayout,9,1,1,1)
		grid.addWidget(self.btnHelp,10,1,1,1)
		grid.addWidget(self.btnAbout,11,1,1,1)	
		
		self.btnLoad.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnSave.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnMSave.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnBulkSave.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnRefresh.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnReplaceid.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnDelete.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnOutput.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnAbout.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnNew.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnData.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnQuery.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnUpload.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnHelp.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.content.setStyleSheet("background-color : rgba(255, 255, 255, 50)")	
		self.btnSC.setIcon(QIcon("QRadioButton::indicator:unchecked {border-image: url(./data/icon/radiobutton_unchecked.svg);}" "QRadioButton::indicator:checked {border-image: url(./source/radiobutton_checked.svg);}"))
		self.btnTC.setIcon(QIcon("QRadioButton::indicator:unchecked {border-image: url(./data/icon/radiobutton_unchecked.svg);}" "QRadioButton::indicator:checked {border-image: url(./source/radiobutton_checked.svg);}"))
		self.btnJP.setIcon(QIcon("QRadioButton::indicator:unchecked {border-image: url(./data/icon/radiobutton_unchecked.svg);}" "QRadioButton::indicator:checked {border-image: url(./source/radiobutton_checked.svg);}"))
		
		self.btnLoad.clicked.connect(self.read_csv)
		self.btnSearch.clicked.connect(self.user_search)
		self.btnSave.clicked.connect(self.add_btnrecord)
		self.btnBulkSave.clicked.connect(self.addinbulk_btnrecord)
		self.btnMSave.clicked.connect(self.addmanually_btnrecord)
		self.btnAbout.clicked.connect(self.show_about)
		self.btnRefresh.clicked.connect(self.refresh_table)
		self.btnReplaceid.clicked.connect(self.replace_id)
		self.btnDelete.clicked.connect(self.delete_record)
		self.btnOutput.clicked.connect(self.output_record)
		self.btnData.clicked.connect(self.data_dashboard)
		self.btnQuery.clicked.connect(self.precise_query)
		self.btnUpload.clicked.connect(self.upload_table)
		self.btnNew.clicked.connect(self.new_table)
		self.btnSC.toggled.connect(self.SC_select)
		self.btnTC.toggled.connect(self.TC_select)
		self.btnJP.toggled.connect(self.JP_select)
		self.btnHelp.clicked.connect(self.show_help)
		
		self.show()
		
	def JP_select(self, event):
		if self.server_la != 'JP':
			self.cf.set('server', 'server_la', 'JP')
			with open('./conf.ini', 'w') as configfile:
				self.cf.write(configfile)
			configfile.close()
		
			print('change to JP')	
			app = QCoreApplication.instance()
			app.quit()
			subprocess.call([sys.executable] + sys.argv)
		
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
		isBulk = False
		if self.server_la == 'SC':
			self.ocr_sc(file_path, img_path, isBulk)
		elif self.server_la == 'TC':
			self.ocr_tc(file_path, img_path, isBulk)
		elif self.server_la == 'JP':
			self.ocr_jp(file_path, img_path, isBulk)
		self.refresh_table(event)
		
	def addmanually_btnrecord(self, event):
		if self.fname == '':
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			file_path = str(self.fname)
			if(file_path == ''):
				print("invaild csv path!")
			print('record: ' + file_path)
			battle_list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
			method = 'manual'
			confirm_dialog = ConfirmDialog()
			self.signal_setbattlelist.emit(battle_list,file_path,method)
			if confirm_dialog.exec() == QDialog.Accepted:
				pass
			self.refresh_table(event)
	
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
			
			isBulk = False
			if self.server_la == 'SC':
				self.ocr_sc(file_path, img_path, isBulk)
			elif self.server_la == 'TC':
				self.ocr_tc(file_path, img_path, isBulk)
			elif self.server_la == 'JP':
				self.ocr_jp(file_path, img_path, isBulk)
			self.refresh_table(event)
				
	def addinbulk_btnrecord(self, event):
		if self.fname == '':
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass	
		else:
			if self.last_filepath == '':
				img_names = QFileDialog.getOpenFileNames(self, '选择截图', '.', '*.png')
			else:
				img_names = QFileDialog.getOpenFileNames(self, '选择截图', self.last_filepath, '*.png')
			print(img_names)
			file_path = str(self.fname)
			img_names = img_names[0]
			img_names.sort()
			logs = []
			
			for img_path in img_names:
				try:
					print(img_path)
					isBulk = True
					if self.server_la == 'SC':
						self.ocr_sc(file_path, img_path, isBulk)
					elif self.server_la == 'TC':
						self.ocr_tc(file_path, img_path, isBulk)
					elif self.server_la == 'JP':
						self.ocr_jp(file_path, img_path, isBulk)
				except:
					logs.append(img_path)
					
			self.refresh_table(event)
			if logs == []:
				print('Done!')
				bulk_dialog = BulkOKDialog()
				if bulk_dialog.exec() == QDialog.Accepted:
					pass
			else:
				print('')
				print('============= WARNING =============')
				print('The following screenshot analysis failed:')
				print(logs)	
				bulk_dialog = BulkLogDialog()
				self.signal_bulklog.emit(logs)
				if bulk_dialog.exec() == QDialog.Accepted:
					pass
				
	def ocr_jp(self, file_path, img_path, isBulk):
		print('record: ' + file_path)
		print('img: ' + img_path)
		if(img_path == ''):
			print("invaild image path!")
		elif(file_path == ''):
			print("invaild csv path!")
		else:
			ocr = PaddleOCR(use_angle_cls=True, lang="japan", show_log=False)
			img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
			cv2.rectangle(img, (1800,790),(1000,870),(216,225,256), -1)
			#cv2.rectangle(img, (140,790),(810,870),(246,247,247), -1)
			cv2.rectangle(img, (1480,250),(1560,300),(216,225,256), -1)
			cv2.rectangle(img, (1480,310),(1830,380),(216,225,256), -1)
				
			try:
				img0 = img[795:920,150:240]
				res0 = ''
				result0 = ocr.ocr(img0, cls=True)
				for i in range(len(result0[0])):
					res0 = res0 + result0[0][i][1][0]
				new_res0 = ''.join(i for i in res0 if i.isalnum())
			except IndexError: 
				new_res0 = ''
				
			try:
				img1 = img[795:920,245:360]
				res1 = ''
				result1 = ocr.ocr(img1, cls=True)
				for i in range(len(result1[0])):
					res1 = res1 + result1[0][i][1][0]
				new_res1 = ''.join(i for i in res1 if i.isalnum())
			except IndexError: 
				new_res1 = ''

			try:
				img2 = img[795:920,365:480]
				res2 = ''
				result2 = ocr.ocr(img2, cls=True)
				for i in range(len(result2[0])):
					res2 = res2 + result2[0][i][1][0]
				new_res2 = ''.join(i for i in res2 if i.isalnum())
			except IndexError: 
				new_res2 = ''

			try:
				img3 = img[795:920,475:590]
				res3 = ''
				result3 = ocr.ocr(img3, cls=True)
				for i in range(len(result3[0])):
					res3 = res3 + result3[0][i][1][0]
				new_res3 = ''.join(i for i in res3 if i.isalnum())
			except IndexError: 
				new_res3 = ''

			try:
				img4 = img[795:920,585:700]
				res4 = ''
				result4 = ocr.ocr(img4, cls=True)
				for i in range(len(result4[0])):
					res4 = res4 + result4[0][i][1][0]
				new_res4 = ''.join(i for i in res4 if i.isalnum())
			except IndexError: 
				new_res4 = ''

			try:
				img5 = img[795:920,695:810]
				res5 = ''
				result5 = ocr.ocr(img5, cls=True)
				for i in range(len(result5[0])):
					res5 = res5 + result5[0][i][1][0]
				new_res5 = ''.join(i for i in res5 if i.isalnum())
			except IndexError: 
				new_res5 = ''

			print(new_res0+' '+new_res1+' '+new_res2+' '+new_res3+' '+new_res4+' '+new_res5)
			
			my_w_res0 = self.jpocr_to_sc(new_res0)
			my_w_res1 = self.jpocr_to_sc(new_res1)
			my_w_res2 = self.jpocr_to_sc(new_res2)
			my_w_res3 = self.jpocr_to_sc(new_res3)
			my_w_res4 = self.jpocr_to_sc(new_res4)
			my_w_res5 = self.jpocr_to_sc(new_res5)
			
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

			try:
				img_u = img[230:390,1030:1860]
				result_u = ocr.ocr(img_u, cls=True)
				new_res_u = result_u[0][0][1][0]
				new_winflag = result_u[0][-1][1][0]
			except IndexError: 
				new_res_u = ''
				new_winflag = 'Win'
				
			if new_winflag == 'Win':
				battle_res = "失败"
			else:
				battle_res = "胜利"
				
			print(new_res_u)
			print(battle_res)

			try:
				em_img0 = img[795:920,1090:1205]
				em_res0 = ''
				em_result0 = ocr.ocr(em_img0, cls=True)
				for i in range(len(em_result0[0])):
					em_res0 = em_res0 + em_result0[0][i][1][0]
				em_new_res0 = ''.join(i for i in em_res0 if i.isalnum())
			except IndexError: 
				em_new_res0 = ''
				
			try:
				em_img1 = img[795:920,1200:1315]
				em_res1 = ''
				em_result1 = ocr.ocr(em_img1, cls=True)
				for i in range(len(em_result1[0])):
					em_res1 = em_res1 + em_result1[0][i][1][0]
				em_new_res1 = ''.join(i for i in em_res1 if i.isalnum())
			except IndexError: 
				em_new_res1 = ''

			try:
				em_img2 = img[795:920,1310:1425]
				em_res2 = ''
				em_result2 = ocr.ocr(em_img2, cls=True)
				for i in range(len(em_result2[0])):
					em_res2 = em_res2 + em_result2[0][i][1][0]
				em_new_res2 = ''.join(i for i in em_res2 if i.isalnum())
			except IndexError: 
				em_new_res2 = ''

			try:
				em_img3 = img[795:920,1420:1540]
				em_res3 = ''
				em_result3 = ocr.ocr(em_img3, cls=True)
				for i in range(len(em_result3[0])):
					em_res3 = em_res3 + em_result3[0][i][1][0]
				em_new_res3 = ''.join(i for i in em_res3 if i.isalnum())
			except IndexError: 
				em_new_res3 = ''

			try:
				em_img4 = img[795:920,1535:1650]
				em_res4 = ''
				em_result4 = ocr.ocr(em_img4, cls=True)
				for i in range(len(em_result4[0])):
					em_res4 = em_res4 + em_result4[0][i][1][0]
				em_new_res4 = ''.join(i for i in em_res4 if i.isalnum())
			except IndexError: 
				em_new_res4 = ''

			try:
				em_img5 = img[795:920,1650:1765]
				em_res5 = ''
				em_result5 = ocr.ocr(em_img5, cls=True)
				for i in range(len(em_result5[0])):
					em_res5 = em_res5 + em_result5[0][i][1][0]
				em_new_res5 = ''.join(i for i in em_res5 if i.isalnum())
			except IndexError: 
				em_new_res5 = ''
				
			print(em_new_res0+' '+em_new_res1+' '+em_new_res2+' '+em_new_res3+' '+em_new_res4+' '+em_new_res5)
	
			w_res0 = self.jpocr_to_sc(em_new_res0)
			w_res1 = self.jpocr_to_sc(em_new_res1)
			w_res2 = self.jpocr_to_sc(em_new_res2)
			w_res3 = self.jpocr_to_sc(em_new_res3)
			w_res4 = self.jpocr_to_sc(em_new_res4)
			w_res5 = self.jpocr_to_sc(em_new_res5)
			
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

			pixel_value_format = img[340,100].tolist()
			print(pixel_value_format)
			if pixel_value_format == [131,98,61]:
				format = "进攻"
			elif pixel_value_format[0]>120 and pixel_value_format[0]<140 and pixel_value_format[1]>90 and pixel_value_format[1]<110 and pixel_value_format[2]>50 and pixel_value_format[2]<70:
				format = "进攻"
			else:
				format = "防守"
			print(format)
			
			battle_list = [new_res_u, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, battle_res, format, img_path]		
			print(battle_list)
			
			if isBulk:
				self.insert_table(battle_list)
			else:
				method = 'auto'
				confirm_dialog = ConfirmDialog()
				self.signal_setbattlelist.emit(battle_list,file_path,method)
				if confirm_dialog.exec() == QDialog.Accepted:
					pass
		
	def ocr_tc(self, file_path, img_path, isBulk):
		print('record: ' + file_path)
		print('img: ' + img_path)
		if(img_path == ''):
			print("invaild image path!")
		elif(file_path == ''):
			print("invaild csv path!")
		else:		
			table_engine = PPStructure(show_log=False, table=True, image_orientation=False,)
			print("ocr is running.")
						
			img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
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
			
			print(new_res0+' '+new_res1+' '+new_res2+' '+new_res3+' '+new_res4+' '+new_res5)
			
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
			
			print(my_new_res0+' '+my_new_res1+' '+my_new_res2+' '+my_new_res3+' '+my_new_res4+' '+my_new_res5)
			
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
						
			battle_list = [new_res6, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, battle_res, format, img_path]
			print(battle_list)
			
			if isBulk:
				self.insert_table(battle_list)
			else:
				method = 'auto'
				confirm_dialog = ConfirmDialog()
				self.signal_setbattlelist.emit(battle_list,file_path,method)
				if confirm_dialog.exec() == QDialog.Accepted:
					pass
				
	def ocr_sc(self, file_path, img_path, isBulk):
		print('record: ' + file_path)
		print('img: ' + img_path)
		if(img_path == ''):
			print("invaild image path!")
		elif(file_path == ''):
			print("invaild csv path!")
		else:		
			table_engine = PPStructure(show_log=False, table=True, image_orientation=False,)
			print("ocr is running.")
						
			#img = cv2.imread(img_path)
			img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
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
			
			print(new_res0+' '+new_res1+' '+new_res2+' '+new_res3+' '+new_res4+' '+new_res5)
			
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
			
			print(my_new_res0+' '+my_new_res1+' '+my_new_res2+' '+my_new_res3+' '+my_new_res4+' '+my_new_res5)
			
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
						
			battle_list = [new_res6, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, battle_res, format, img_path]
		
			if isBulk:
				self.insert_table(battle_list)
			else:
				method = 'auto'
				confirm_dialog = ConfirmDialog()
				self.signal_setbattlelist.emit(battle_list,file_path,method)
				if confirm_dialog.exec() == QDialog.Accepted:
					pass
			
	def show_csv(self, df_img):	
		self.content.clear()
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
					<th>{{ Bv }}</th>
					<th>{{ Link }}</th>
					<th>{{ ESpecial1 }}</th>
					<th>{{ ESpecial2 }}</th>
				</tr>
				<tr>
					<th colspan="9">{{ Note }}</th>
				</tr>
			'''


			if pd.isnull(df_img.iloc[num,17]):
				userid_word = '<br><br>' + str(df_img.iloc[num,0])
			else:
				userid_word = '<br>' + str(df_img.iloc[num,0]) + '<br>' + str(df_img.iloc[num,17])
				
			if pd.isnull(df_img.iloc[num,18]):
				link_word = ''
			else:
				link_word = '<br><br><a href="' + str(df_img.iloc[num,18]) + '">素材</a>'
				
			if pd.isnull(df_img.iloc[num,19]):
				bv_word = ''
			else:
				bv_word = '<br><br><a href="https://www.bilibili.com/video/' + str(df_img.iloc[num,19]) + '">BV</a>'
				
			if pd.isnull(df_img.iloc[num,16]):
				note_word = ''
			else:
				note_word = str(df_img.iloc[num,16])
				
			template_data = Template(template_string_data)		
			html_data = template_data.render(
				UserId = userid_word,
				Date = '<br><br>' + str(df_img.iloc[num,1]),				
				FAttacker1 = '<img src=' + './data/images/stud/' + df_img.iloc[num,2] + '.png width=80/>',
				FAttacker2 = '<img src=' + './data/images/stud/' + df_img.iloc[num,3] + '.png width=80/>',
				FAttacker3 = '<img src=' + './data/images/stud/' + df_img.iloc[num,4] + '.png width=80/>',
				FAttacker4 = '<img src=' + './data/images/stud/' + df_img.iloc[num,5] + '.png width=80/>',
				FSpecial1 = '<img src=' + './data/images/stud/' + df_img.iloc[num,6] + '.png width=80/>',
				FSpecial2 = '<img src=' + './data/images/stud/' + df_img.iloc[num,7] + '.png width=80/>',
				Formation = '<br><img src=' + './data/images/' + df_img.iloc[num,8] + '.png width=80/>',
				EAttacker1 = '<img src=' + './data/images/stud/' + df_img.iloc[num,9] + '.png width=80/>',
				EAttacker2 = '<img src=' + './data/images/stud/' + df_img.iloc[num,10] + '.png width=80/>',
				EAttacker3 = '<img src=' + './data/images/stud/' + df_img.iloc[num,11] + '.png width=80/>',
				EAttacker4 = '<img src=' + './data/images/stud/' + df_img.iloc[num,12] + '.png width=80/>',
				ESpecial1 = '<img src=' + './data/images/stud/' + df_img.iloc[num,13] + '.png width=80/>',
				ESpecial2 = '<img src=' + './data/images/stud/' + df_img.iloc[num,14] + '.png width=80/>',
				Result = '<br><img src=' + './data/images/' + df_img.iloc[num,15] + '.png width=80/>',
				Link = link_word,
				Bv = bv_word,
				Me = '<br><br>' + '我的阵容',
				Note = note_word,
				space = ''
			)
			self.content.append(html_data)
			self.content.append('\n\n')
		
	def insert_table(self, battle_list):
			print('insert: ')
			if battle_list[0] != '':
				userId = battle_list[0]
			else:
				userId = 'NoData'
				
			if battle_list[13] != '':
				result = battle_list[13]
			else:
				result = '胜利'
			
			Fatk1 = self.sc_to_code(battle_list[7])
			Fatk2 = self.sc_to_code(battle_list[8])
			Fatk3 = self.sc_to_code(battle_list[9])
			Fatk4 = self.sc_to_code(battle_list[10])
			Fspl1 = self.sc_to_code(battle_list[11])
			Fspl2 = self.sc_to_code(battle_list[12])
			Eatk1 = self.sc_to_code(battle_list[1])
			Eatk2 = self.sc_to_code(battle_list[2])
			Eatk3 = self.sc_to_code(battle_list[3])
			Eatk4 = self.sc_to_code(battle_list[4])
			Espl1 = self.sc_to_code(battle_list[5])
			Espl2 = self.sc_to_code(battle_list[6])
			date = str(datetime.date.today())
			note = ''
			title = ''
			bv = ''
			check = '0'

			if battle_list[14] != '':
				formation = battle_list[14]
			else:
				formation = '进攻'
				
			if battle_list[15] != '':
				link = battle_list[15]
				img_str = battle_list[15].split('/')[-1]
				if img_str[0:4] == 'MuMu':
					date = img_str[7:11] + '-' + img_str[11:13] + '-' + img_str[13:15]
			else:
				link = ''
			
			file_path = str(self.fname)
			with open(file_path, "a", encoding="utf-8", newline="") as f:
				wf = csv.writer(f)
				new_data = [userId,date,Fatk1,Fatk2,Fatk3,Fatk4,Fspl1,Fspl2,formation,Eatk1,Eatk2,Eatk3,Eatk4,Espl1,Espl2,result,note,title,link,bv,check]
				wf.writerow(new_data)
				f.close()		
		
	def upload_table(self, event):
		fname_r, fpath= QFileDialog.getOpenFileName(self, '选择csv记录', './table', '*.csv')
		if fname_r != '':
			data = {'file': open(fname_r, 'rb')}
			rr = requests.post(web_url + '//upload', files=data)
			print(rr.status_code)
			print(rr.text)
			webbrowser.open(web_url)
		else:
			print('No file was seclected!')
		
	def read_csv(self, event):
		fname_r, fpath= QFileDialog.getOpenFileName(self, '选择csv记录', './table', '*.csv')
		if fname_r == '' :
			print(self.fname)
			pass
		else:
			self.fname = fname_r
			print(self.fname)
			df = pd.read_csv(self.fname)		
			if list(df) != ['UserId', 'Date', 'FAttacker1', 'FAttacker2', 'FAttacker3', 'FAttacker4', 'FSpecial1', 'FSpecial2', 'Formation', 'EAttacker1', 'EAttacker2', 'EAttacker3', 'EAttacker4', 'ESpecial1', 'ESpecial2', 'Result', 'Note', 'Title', 'Link', 'Bv', 'Check']:
				block_list =[]
				for i in range(len(df)):
					block_list.append('')
				df['Note'] = block_list
				df['Title'] = block_list
				df['Link'] = block_list
				df['Bv'] = block_list
				df['Check'] = block_list
				df.to_csv(self.fname, index=False)
				print('The file format has been updated.')
			
			self.content.clear()
			df_img = df		
			self.show_csv(df_img)
			winrate = '{:.2%}'.format(self.cal_winrate(df_img))
			new_wr_word = ' 胜率：' + winrate
			self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
			
	def refresh_table(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			print(self.fname)
			df = pd.read_csv(self.fname)	
			self.content.clear()
			df_img = df
			self.show_csv(df_img)
			winrate = '{:.2%}'.format(self.cal_winrate(df_img))
			new_wr_word = ' 胜率：' + winrate
			self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
			
	def replace_id(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			replace_dialog = ReplaceDialog()
			file_path = str(self.fname)
			print(file_path)
			self.signal_filename.emit(file_path)
			if replace_dialog.exec() == QDialog.Accepted:
				pass
				
	def delete_record(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			self.delete_dialog = DeleteDialog()
			file_path = str(self.fname)
			print(file_path)
			self.signal_filename.emit(file_path)
			if self.delete_dialog.exec() == QDialog.Accepted:
				pass
			
	def	output_record(self, event):
		if self.df_output.empty:
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			root = Tk()
			root.withdraw()		
			file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='保存记录', filetypes=[('CSV Document', '*.csv')])		
			if file_path != '':
				self.df_output.to_csv(file_path, index=False, encoding="utf-8")
				self.df_output = pd.DataFrame()
				print('Output has done.')
	
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
				
	def precise_query(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			query_dialog = QueryDialog()
			query_dialog.signal_setquery.connect(self.get_query)
			file_path = str(self.fname)
			self.signal_filename.emit(file_path)
			if query_dialog.exec() == QDialog.Accepted:
				pass	
				
	def data_dashboard(self, event):
		if self.fname == '' :
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:
			dash_dialog = DashboardDialog()
			dash_dialog.signal_setstu.connect(self.get_stu)
			file_path = str(self.fname)
			self.signal_filename.emit(file_path)
			if dash_dialog.exec() == QDialog.Accepted:
				pass			

	def new_table(self, event):
		new_dialog = NewCsvDialog()
		if new_dialog.exec() == QDialog.Accepted:
			pass					

	def paintEvent(self, event):		
		painter = QPainter(self)
		if self.server_la == 'SC':
			pixmap = QPixmap("./data/images/bg.png")
		elif self.server_la == 'TC':
			pixmap = QPixmap("./data/images/bg_tc.png")
		elif self.server_la == 'JP':
			pixmap = QPixmap("./data/images/bg_jp.png")
		
		painter.drawPixmap(self.rect(), pixmap)
		
	def get_query(self, query_list):
		print('get query:')
		print(query_list)
		#query_list = [userId, result, formation, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, title]
		userId = query_list[0]
		result = query_list[1]
		formation = query_list[2]
		Fatk1 = query_list[3]
		Fatk2 = query_list[4]
		Fatk3 = query_list[5]
		Fatk4 = query_list[6]
		Fspl1 = query_list[7]
		Fspl2 = query_list[8]
		Eatk1 = query_list[9]
		Eatk2 = query_list[10]
		Eatk3 = query_list[11]
		Eatk4 = query_list[12]
		Espl1 = query_list[13]
		Espl2 = query_list[14]
		title = query_list[15]
		
		df = pd.read_csv(self.fname)
		if userId != '1NoData':
			df = df.query('UserId == @userId')
		if result != '任意':
			df = df.query('Result == @result')
		if formation != '任意':
			df = df.query('Formation == @formation')	
		if Fatk1 != '1NoData':
			df = df.query('FAttacker1 == @Fatk1')
		if Fatk2 != '1NoData':
			df = df.query('FAttacker2 == @Fatk2')
		if Fatk3 != '1NoData':
			df = df.query('FAttacker3 == @Fatk3')
		if Fatk4 != '1NoData':
			df = df.query('FAttacker4 == @Fatk4')
		if Fspl1 != '1NoData':
			df = df.query('FSpecial1 == @Fspl1 | FSpecial2 == @Fspl1')
		if Fspl2 != '1NoData':
			df = df.query('FSpecial2 == @Fspl2 | FSpecial1 == @Fspl2')
		if Eatk1 != '1NoData':
			df = df.query('EAttacker1 == @Eatk1')
		if Eatk2 != '1NoData':
			df = df.query('EAttacker2 == @Eatk2')
		if Eatk3 != '1NoData':
			df = df.query('EAttacker3 == @Eatk3')
		if Eatk4 != '1NoData':
			df = df.query('EAttacker4 == @Eatk4')
		if Espl1 != '1NoData':
			df = df.query('ESpecial1 == @Espl1 | ESpecial2 == @Espl1')
		if Espl2 != '1NoData':
			df = df.query('ESpecial2 == @Espl2 | ESpecial1 == @Espl2')	
		if title != '':
			df = df[df['Title'].str.contains(title, na=False)]
		
		print(df)
		self.show_csv(df)
		self.df_output = df.copy()
		winrate = '{:.2%}'.format(self.cal_winrate(df))
		new_wr_word = " 胜率：" + winrate
		self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
			
	def get_stu(self, stuid_list0, stuid_list1):
		self.content.clear()
		f_namelist = []
		e_namelist = []
		f_printlist = []
		e_printlist = []
		f_namelist_length = 0
		e_namelist_length = 0
		f_str_print = ''
		e_str_print = ''
		
		print('get')
		if stuid_list0 != []:
			stuid_list0 = list(filter(None, stuid_list0))
		if stuid_list1 != []:
			stuid_list1 = list(filter(None, stuid_list1))
		if stuid_list0 != []:
			for stuid in stuid_list0:
				f_printlist.append(' ')
				f_printlist.append(stuid)
				stuid = self.nickname_to_code(stuid)
				f_namelist.append(stuid)
			try:
				stuid_list0 = list(filter('', stuid_list0))
			except TypeError:
				print(' ')
			print(f_namelist)		
		if stuid_list1 != []:
			for stuid in stuid_list1:
				e_printlist.append(' ')
				e_printlist.append(stuid)
				stuid = self.nickname_to_code(stuid)
				e_namelist.append(stuid)
			try:
				stuid_list1 = list(filter('', stuid_list1))
			except TypeError:
				print(' ')
			print(e_namelist)
		
		if stuid_list0 != []:
			f_str_print = str(f_printlist)
			f_str_print = f_str_print.replace('[', '')
			f_str_print = f_str_print.replace(']', '')
			f_str_print = f_str_print.replace("'", "")
			f_str_print = f_str_print.replace(',', '')

		wr_word = '<i>' + f_str_print + '</i>'
		
		if stuid_list1 != []:
			e_str_printlist = str(e_printlist)
			e_str_printlist = e_str_printlist.replace('[', '')
			e_str_printlist = e_str_printlist.replace(']', '')
			e_str_printlist = e_str_printlist.replace("'", "")
			e_str_printlist = e_str_printlist.replace(',', '')
			wr_word1 = wr_word + ' 对阵<i>' + e_str_printlist + '</i>'
		else:
			wr_word1 = wr_word + ' 对阵'
		
		df = pd.read_csv(self.fname)
		if stuid_list0 != []:
			f_namelist_length = len(f_namelist) - 1		
		if stuid_list1 != []:
			e_namelist_length = len(e_namelist) - 1
		if stuid_list0 != []:
			self.search_stu_f(df, f_namelist, f_namelist_length, wr_word, stuid_list1, e_namelist, e_namelist_length, wr_word1)
		else:
			self.search_stu_e(df, e_namelist, e_namelist_length, wr_word1)
				
	def search_stu_f(self, df, f_namelist, f_namelist_length, wr_word, stuid_list1, e_namelist, e_namelist_length, wr_word1):
		self.content.clear()
		df = df.copy()
		if f_namelist_length == -1:
			if stuid_list1 == []:
				winrate = '{:.2%}'.format(self.cal_winrate(df))
				new_wr_word = wr_word + ' 胜率：' + winrate
				self.show_csv(df)
				self.df_output = df.copy()
				self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
			elif stuid_list1 != []:
				self.search_stu_e(df, e_namelist, e_namelist_length, wr_word1)
		else:
			tag = f_namelist[f_namelist_length]
			res = df.query('FAttacker1 == @tag | FAttacker2 == @tag | FAttacker3 == @tag | FAttacker4 == @tag | FSpecial1 == @tag | FSpecial2 == @tag')
			self.search_stu_f(res,f_namelist, f_namelist_length-1,wr_word,stuid_list1, e_namelist, e_namelist_length, wr_word1)	
	
	def search_stu_e(self, df, e_namelist, e_namelist_length, wr_word1):
		self.content.clear()
		df = df.copy()
		if e_namelist_length == -1:
			winrate = '{:.2%}'.format(self.cal_winrate(df))
			new_wr_word = wr_word1 + " 胜率：" + winrate			
			self.show_csv(df)
			self.df_output = df.copy()
			self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
		else:
			tag = e_namelist[e_namelist_length]
			res = df.query('EAttacker1 == @tag | EAttacker2 == @tag | EAttacker3 == @tag | EAttacker4 == @tag | ESpecial1 == @tag | ESpecial2 == @tag')
			self.search_stu_e(res,e_namelist, e_namelist_length-1,wr_word1)	
	
	def cal_winrate(self, res):
		try:
			win_count = res['Result'].value_counts()['胜利']
		except KeyError:
			win_count = 0
		total_count = len(res)
		print('win: ' + str(win_count))
		print('total: ' + str(total_count))
		winrate = win_count / total_count
		return winrate
		
	def get_id(self,userid):
		self.userid = userid
		print('get ' + self.userid)
		self.content.clear()
		self.content.append(userid)
		
		df = pd.read_csv(self.fname)
		df_img = df[df['UserId'] == userid]
		print(df_img)
		self.show_csv(df_img)
		self.df_output = df_img.copy()
		winrate = '{:.2%}'.format(self.cal_winrate(df_img))
		new_wr_word = ' 胜率：' + winrate
		self.content.append('<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" ><tr><td><font color="black"><h2>'+ new_wr_word+'</h2>')
			
	def sc_to_code(self,stud):
		stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
		return stud_dict[stud]
		
	def nickname_to_code(self,stud):
		stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
		try:
			stud_name = stud_dict[stud]
		except KeyError:
			stud_name = ''
		return stud_name
	
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
	
	def jpocr_to_sc(self,stud):
		stud_dict = pd.read_json('./data/studstr_jpocr2sc.json', typ='series')
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
		self.file_path = ''
		self.method = ''
		self.asset_link = ''
		self.cf = configparser.ConfigParser()
		self.cf.read("./conf.ini")
		self.last_filepath = self.cf.get("filepath","asset_path")
		self.initUI()
		window.signal_setbattlelist.connect(self.get_battlelist)
		try:
			window.delete_dialog.signal_setbattlelist.connect(self.get_battlelist)
		except:
			print('')
		
		
	def initUI(self):
		self.setFixedSize(600, 640)  
		self.setWindowTitle('确认数据')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
		stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
		completer_words = list(stud_dict.keys())
		completer = QCompleter(completer_words)
		completer.setFilterMode(Qt.MatchContains)
		
		self.btnLink = QPushButton('链接素材（可选）',self)
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
		self.label_date = QLabel('对战日期', self)
		self.label_format = QLabel('编队模式', self)
		self.label_bv = QLabel('BV号（选填）', self)
		self.label_title = QLabel('标题（选填）', self)
		self.label_note = QLabel('备注（选填）', self)
		
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
		self.dateEdit = QDateEdit()
		self.ComboBox_format = QComboBox()
		self.lineEdit_bv = QLineEdit()
		self.lineEdit_title = QLineEdit()
		self.lineEdit_note = QLineEdit()
		
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
		self.dateEdit.setDisplayFormat('yyyy-MM-dd')
		self.dateEdit.setStyleSheet("QDateEdit::down-arrow {image: url(./data/icon/down_arrow.svg);}")
		self.dateEdit.setCalendarPopup(True)
		self.dateEdit.setDate(QDate.currentDate())
		
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
		
		grid.addWidget(self.label_bv,9,2,1,1)
		grid.addWidget(self.label_user,9,3,1,1)
		grid.addWidget(self.label_res,9,4,1,1)
		grid.addWidget(self.lineEdit_bv,10,2,1,1)
		grid.addWidget(self.lineEdit_user,10,3,1,1)
		grid.addWidget(self.ComboBox_res,10,4,1,1)
		
		grid.addWidget(self.label_date,11,3,1,1)
		grid.addWidget(self.label_format,11,4,1,1)
		grid.addWidget(self.dateEdit,12,3,1,1)
		grid.addWidget(self.ComboBox_format,12,4,1,1)
		
		grid.addWidget(self.label_title,13,3,1,1)
		grid.addWidget(self.label_note,13,4,1,1)
		grid.addWidget(self.lineEdit_title,14,3,1,1)
		grid.addWidget(self.lineEdit_note,14,4,1,1)
		
		grid.addWidget(self.btnLink,15,3,1,1)
		grid.addWidget(self.btnOk,15,4,1,1)

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
		self.label_bv.setAlignment(Qt.AlignCenter)
		self.label_user.setAlignment(Qt.AlignCenter)
		self.label_res.setAlignment(Qt.AlignCenter)
		self.label_date.setAlignment(Qt.AlignCenter)
		self.label_format.setAlignment(Qt.AlignCenter)
		self.label_title.setAlignment(Qt.AlignCenter)
		self.label_note.setAlignment(Qt.AlignCenter)
		
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
		self.label_bv.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_user.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_res.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_date.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_format.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_title.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_note.setStyleSheet("font-weight:bold;font-size:16px")
				
		self.btnLink.setStyleSheet("background-color : rgba(176,196,222,1)")
		self.btnOk.setStyleSheet("background-color : rgba(176,196,222,1)")
		
		self.btnLink.clicked.connect(self.link_asset)
		self.btnOk.clicked.connect(self.insert_table)
		self.btnOk.clicked.connect(self.close)
		
		self.show()
		
	def get_battlelist(self, battle_list, file_name, method):
		if len(battle_list) == 16:
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
			self.asset_link = battle_list[15]
		elif len(battle_list) == 19:
			print('get:')
			print(battle_list)
			self.lineEdit_user.setText(battle_list[0])
			self.lineEdit_e1.setText(self.code_to_sc(battle_list[1]))
			self.lineEdit_e2.setText(self.code_to_sc(battle_list[2]))
			self.lineEdit_e3.setText(self.code_to_sc(battle_list[3]))
			self.lineEdit_e4.setText(self.code_to_sc(battle_list[4]))
			self.lineEdit_e5.setText(self.code_to_sc(battle_list[5]))
			self.lineEdit_e6.setText(self.code_to_sc(battle_list[6]))
			self.lineEdit_f1.setText(self.code_to_sc(battle_list[7]))
			self.lineEdit_f2.setText(self.code_to_sc(battle_list[8]))
			self.lineEdit_f3.setText(self.code_to_sc(battle_list[9]))
			self.lineEdit_f4.setText(self.code_to_sc(battle_list[10]))
			self.lineEdit_f5.setText(self.code_to_sc(battle_list[11]))
			self.lineEdit_f6.setText(self.code_to_sc(battle_list[12]))
			self.ComboBox_res.setCurrentText(battle_list[13])
			self.ComboBox_format.setCurrentText(battle_list[14])
			self.lineEdit_note.setText(str(battle_list[15]))
			self.lineEdit_title.setText(str(battle_list[16]))	
			self.asset_link = str(battle_list[17])
			self.lineEdit_bv.setText(str(battle_list[18]))

		self.file_path = file_name
		self.method = method
		df = pd.read_csv(self.file_path)
		user_list = list(set(df['UserId']))
		completer_user = QCompleter(user_list)
		completer_user.setFilterMode(Qt.MatchContains)
		self.lineEdit_user.setCompleter(completer_user)
		
	def link_asset(self):		
		if self.last_filepath == '':
			fname_r, fpath = QFileDialog.getOpenFileName(self, '选择视频或文件', '', '*.png *.jpg *.gif *.avi *.mp4 *.mov *.wmv *.mkv *.flv')
		else:
			fname_r, fpath = QFileDialog.getOpenFileName(self, '选择视频或文件', self.last_filepath, '*.png *.jpg *.gif *.avi *.mp4 *.mov *.wmv *.mkv *.flv')		
		print(fname_r)
		
		if fname_r != '':
			self.last_filepath = fname_r
			self.asset_link = fname_r
		self.cf.set('filepath', 'asset_path', fname_r)
		with open('./conf.ini', 'w') as configfile:
			self.cf.write(configfile)
		configfile.close()

	def code_to_sc(self, stud):
		if stud != '':
			stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
			for key, value in stud_dict.items():
				if value == stud:
					return key
			return '1NoData'
		else:
			return '1NoData'
			
	def sc_to_code(self, stud, method):
		if method != 'manual':
			if stud != '':
				stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
				return stud_dict[stud]
			else:
				return '1NoData'
		else:
			if stud != '':
				stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
				return stud_dict[stud]
			else:
				return '1NoData'
		
	def insert_table(self, event):
		print('insert: ')
		if self.lineEdit_user.text() != '':
			userId = self.lineEdit_user.text()
		else:
			userId = 'NoData'
			
		if self.ComboBox_res.currentText() != '':
			result = self.ComboBox_res.currentText()
		else:
			result = '胜利'
		
		Fatk1 = self.sc_to_code(self.lineEdit_f1.text(), self.method)
		Fatk2 = self.sc_to_code(self.lineEdit_f2.text(), self.method)
		Fatk3 = self.sc_to_code(self.lineEdit_f3.text(), self.method)
		Fatk4 = self.sc_to_code(self.lineEdit_f4.text(), self.method)
		Fspl1 = self.sc_to_code(self.lineEdit_f5.text(), self.method)
		Fspl2 = self.sc_to_code(self.lineEdit_f6.text(), self.method)
		Eatk1 = self.sc_to_code(self.lineEdit_e1.text(), self.method)
		Eatk2 = self.sc_to_code(self.lineEdit_e2.text(), self.method)
		Eatk3 = self.sc_to_code(self.lineEdit_e3.text(), self.method)
		Eatk4 = self.sc_to_code(self.lineEdit_e4.text(), self.method)
		Espl1 = self.sc_to_code(self.lineEdit_e5.text(), self.method)
		Espl2 = self.sc_to_code(self.lineEdit_e6.text(), self.method)
		date = self.dateEdit.dateTime()
		note = self.lineEdit_note.text()
		title = self.lineEdit_title.text()
		link = self.asset_link
		bv = self.lineEdit_bv.text()
		check = '0'

		if self.ComboBox_format.currentText() != '':
			formation = self.ComboBox_format.currentText()
		else:
			formation = '进攻'
		
		with open(self.file_path, "a", encoding="utf-8", newline="") as f:
			wf = csv.writer(f)
			new_data = [userId,date.toString("yyyy-MM-dd"),Fatk1,Fatk2,Fatk3,Fatk4,Fspl1,Fspl2,formation,Eatk1,Eatk2,Eatk3,Eatk4,Espl1,Espl2,result,note,title,link,bv,check]
			wf.writerow(new_data)
			f.close()

	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/confirm.png")
		painter.drawPixmap(self.rect(), pixmap)

class QueryDialog(QDialog):
	signal_setquery = Signal(list)
	
	def __init__(self):
		super().__init__()
		self.method = 'manual'
		self.initUI()
		window.signal_filename.connect(self.get_file_name)
		
	def initUI(self):
		self.setFixedSize(600, 540)  
		self.setWindowTitle('查询数据（任意则置空）')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
		stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
		completer_words = list(stud_dict.keys())
		completer = QCompleter(completer_words)
		completer.setFilterMode(Qt.MatchContains)
		
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
		self.label_title = QLabel('标题字符匹配', self)
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
		self.lineEdit_title = QLineEdit()
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
		self.ComboBox_res.addItems(["任意", "胜利", "失败"])
		self.ComboBox_res.setStyleSheet("QComboBox::down-arrow {image: url(./data/icon/down_arrow.svg);}")
		self.ComboBox_format.setEditable(True)
		self.ComboBox_format.addItems(["任意", "进攻", "防守"])
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
		
		grid.addWidget(self.label_title,11,3,1,1)
		grid.addWidget(self.lineEdit_title,12,3,1,1)
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
		self.label_title.setAlignment(Qt.AlignCenter)
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
		self.label_title.setStyleSheet("font-weight:bold;font-size:16px")
		self.label_format.setStyleSheet("font-weight:bold;font-size:16px")
				
		self.btnOk.setStyleSheet("background-color : rgba(176,196,222,1)")
		
		self.btnOk.clicked.connect(self.querylist_emit)
		self.btnOk.clicked.connect(self.close)
		
		self.show()
		
	def querylist_emit(self, event):
		if self.lineEdit_user.text() != '':
			userId = self.lineEdit_user.text()
		else:
			userId = '1NoData'
			
		if self.ComboBox_res.currentText() != '':
			result = self.ComboBox_res.currentText()
		else:
			result = '1NoData'
			
		Fatk1 = self.sc_to_code(self.lineEdit_f1.text(), self.method)
		Fatk2 = self.sc_to_code(self.lineEdit_f2.text(), self.method)
		Fatk3 = self.sc_to_code(self.lineEdit_f3.text(), self.method)
		Fatk4 = self.sc_to_code(self.lineEdit_f4.text(), self.method)
		Fspl1 = self.sc_to_code(self.lineEdit_f5.text(), self.method)
		Fspl2 = self.sc_to_code(self.lineEdit_f6.text(), self.method)
		Eatk1 = self.sc_to_code(self.lineEdit_e1.text(), self.method)
		Eatk2 = self.sc_to_code(self.lineEdit_e2.text(), self.method)
		Eatk3 = self.sc_to_code(self.lineEdit_e3.text(), self.method)
		Eatk4 = self.sc_to_code(self.lineEdit_e4.text(), self.method)
		Espl1 = self.sc_to_code(self.lineEdit_e5.text(), self.method)
		Espl2 = self.sc_to_code(self.lineEdit_e6.text(), self.method)
		title = self.lineEdit_title.text()
		
		if self.ComboBox_format.currentText() != '':
			formation = self.ComboBox_format.currentText()
		else:
			formation = '1NoData'
			
		query_list = [userId, result, formation, Fatk1, Fatk2, Fatk3, Fatk4, Fspl1, Fspl2, Eatk1, Eatk2, Eatk3, Eatk4, Espl1, Espl2, title]
		self.signal_setquery.emit(query_list)
		
	def get_file_name(self, file_path):
		df = pd.read_csv(file_path)	
		user_list = list(set(df['UserId']))
		completer_user = QCompleter(user_list)
		completer_user.setFilterMode(Qt.MatchContains)
		self.lineEdit_user.setCompleter(completer_user)
		
	def sc_to_code(self, stud, method):
		if method != 'manual':
			if stud != '':
				stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
				return stud_dict[stud]
			else:
				return '1NoData'
		else:
			if stud != '':
				stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
				return stud_dict[stud]
			else:
				return '1NoData'
				
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/query.png")
		painter.drawPixmap(self.rect(), pixmap)

class DashboardDialog(QDialog):
	signal_setstu = Signal(list, list)
	
	def __init__(self):
		super().__init__()
		self.initUI()
		window.signal_filename.connect(self.get_file_name)
		
	def initUI(self):
		self.setFixedSize(400, 400)  
		self.setWindowTitle('查询我方学生胜率')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		
		self.label0 = QLabel('请输入官中学生名组合，少于三个则不填留空。', self)
		self.label1 = QLabel('我方', self)
		self.lineEdit0 = QLineEdit(self)
		self.lineEdit1 = QLineEdit(self)
		self.lineEdit2 = QLineEdit(self)
		self.label2 = QLabel('敌方', self)
		self.lineEdit3 = QLineEdit(self)
		self.lineEdit4 = QLineEdit(self)
		self.lineEdit5 = QLineEdit(self)
		
		self.btnOk = QPushButton('查询',self)
		
		self.btnOk.clicked.connect(self.set_stuid)
		self.btnOk.clicked.connect(self.close)	
		
		RBLayout0 = QHBoxLayout()
		RBLayout0.addWidget(self.lineEdit0)
		RBLayout0.addWidget(self.lineEdit1)
		RBLayout0.addWidget(self.lineEdit2)
		RBLayout1 = QHBoxLayout()
		RBLayout1.addWidget(self.lineEdit3)
		RBLayout1.addWidget(self.lineEdit4)
		RBLayout1.addWidget(self.lineEdit5)
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label0)
		vbox.addWidget(self.label1)
		vbox.addLayout(RBLayout0)
		vbox.addWidget(self.label2)
		vbox.addLayout(RBLayout1)
		vbox.addWidget(self.btnOk)
		vbox.addStretch(1)
		self.setLayout(vbox)
		self.show()
		
	def get_file_name(self, file_path):
		df = pd.read_csv(file_path)		
		stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
		completer_words = list(stud_dict.keys())
		completer = QCompleter(completer_words)
		completer.setFilterMode(Qt.MatchContains)
		self.lineEdit0.setCompleter(completer)
		self.lineEdit1.setCompleter(completer)
		self.lineEdit2.setCompleter(completer)
		self.lineEdit3.setCompleter(completer)
		self.lineEdit4.setCompleter(completer)
		self.lineEdit5.setCompleter(completer)
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/search.png")
		painter.drawPixmap(self.rect(), pixmap)
				
	def set_stuid(self):
		stuid0 = self.lineEdit0.text()
		stuid1 = self.lineEdit1.text()
		stuid2 = self.lineEdit2.text()
		stuid3 = self.lineEdit3.text()
		stuid4 = self.lineEdit4.text()
		stuid5 = self.lineEdit5.text()
		stuid_list0 = [stuid0, stuid1, stuid2]
		print(stuid_list0)
		stuid_list1 = [stuid3, stuid4, stuid5]
		print(stuid_list1)
		self.signal_setstu.emit(stuid_list0, stuid_list1)
			
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

class ReplaceDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()
		window.signal_filename.connect(self.get_file_name)
		
		
	def initUI(self):
		self.setFixedSize(400, 400)  
		self.setWindowTitle('替换用户ID')
		
		self.fname = ''
		
		self.label = QLabel('请输入需要被替换的ID', self)
		self.lineEdit = QLineEdit(self)
		self.label1 = QLabel('请输入需要替换后的ID', self)
		self.lineEdit1 = QLineEdit(self)
		self.btnOk = QPushButton('替换',self)
		
		self.btnOk.clicked.connect(self.replace_id)
		self.btnOk.clicked.connect(self.close)	
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label)
		vbox.addWidget(self.lineEdit)
		vbox.addWidget(self.label1)
		vbox.addWidget(self.lineEdit1)
		vbox.addWidget(self.btnOk)
		vbox.addStretch(1)
		self.setLayout(vbox)
		self.show()
		
	def get_file_name(self, file_path):
		df = pd.read_csv(file_path)
		self.fname = file_path
		user_list = list(set(df['UserId']))
		completer = QCompleter(user_list)
		completer.setFilterMode(Qt.MatchContains)
		self.lineEdit.setCompleter(completer)
		self.lineEdit1.setCompleter(completer)
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/search.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	def replace_id(self):
		df = pd.read_csv(self.fname)
		df['UserId'] = df['UserId'].replace(self.lineEdit.text(), self.lineEdit1.text())
		print('replace: ' + self.lineEdit.text() + ' --> ' +  self.lineEdit1.text())
		df.to_csv(self.fname, index=False)
		self.fname = ''

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
				
class DeleteDialog(QDialog):
	signal_setbattlelist = Signal(list,str,str)
	
	def __init__(self):
		super().__init__()
		self.fname = ''
		self.delete_index = []
		window.signal_filename.connect(self.get_file_name)
		self.initUI()
		self.show()
		
	def initUI(self):
		self.resize(600, 540)  
		self.setWindowTitle('删除数据')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		
		self.btnOk = QPushButton('确认修改',self)
		self.btnOk.setProperty('class', 'danger')
		self.btnOk.clicked.connect(self.delete_row)
		self.btnOk.clicked.connect(self.close)
		self.btnCancel = QPushButton('取消修改',self)
		self.btnCancel.clicked.connect(self.close)
		
		self.btnCancel.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		self.btnOk.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		
	def get_file_name(self, file_path):
		print(file_path)
		
		self.fname = file_path
		
		df = pd.read_csv(self.fname)
		df_length = len(df)
		
		self.model = QStandardItemModel()
		self.model.setHorizontalHeaderLabels(['','', 'ID', '日期', '我方', '', '', '', '', '', '模式', '敌方', '', '', '', '', '', '结果','备注','标题','素材','BV'])
		
		for row in range(df_length):
			for column in range(2,22):
				if pd.isnull(df.iloc[row,column-2]):
					item_word = ''
				else:
					item_word = df.iloc[row,column-2]	
				item = QStandardItem(item_word)
				self.model.setItem(row, column, item)
					
		self.tableView = QTableView()
		self.tableView.setShowGrid(False)
		self.tableView.setModel(self.model)
		self.tableView.setStyleSheet("background-color:transparent")
		self.tableView.scrollToBottom()
		header1 = self.tableView.horizontalHeader()
		header1.setStyleSheet("::section{background-color: #87CEFA;}")
		header2 = self.tableView.verticalHeader()
		header2.setStyleSheet("::section{background-color: #87CEFA;}")
		
		bottom_layout = QHBoxLayout()
		bottom_layout.addStretch(1)
		bottom_layout.addWidget(self.btnCancel)
		bottom_layout.addWidget(self.btnOk)

		layout = QVBoxLayout()
		layout.addWidget(self.tableView)
		layout.addLayout(bottom_layout)
		self.setLayout(layout)		
		
		for row in range(df_length):
			btn_d = QPushButton('删除')
			btn_d.setProperty('row', row)
			btn_d.setProperty('column', 0)
			btn_d.clicked.connect(self.on_button_clicked)		
			index = self.model.index(row, 0, QModelIndex())
			self.tableView.setIndexWidget(index, btn_d)	
			
		for row in range(df_length):
			btn_m = QPushButton('修改')
			btn_m.setProperty('row', row)
			btn_m.setProperty('column', 1)
			btn_m.clicked.connect(self.modify_button_clicked)	
			index = self.model.index(row, 1, QModelIndex())
			self.tableView.setIndexWidget(index, btn_m)	
	
		
	def modify_button_clicked(self, event):
		sender = self.sender()
		row = sender.property('row')
		column = sender.property('column')
		index = self.model.index(row, column, QModelIndex())
		df = pd.read_csv(self.fname)
		
		record_list = list(df.iloc[row])
		battle_list = [record_list[0], record_list[9], record_list[10], record_list[11], record_list[12], record_list[13], record_list[14], record_list[2], record_list[3], record_list[4], record_list[5], record_list[6], record_list[7], record_list[15], record_list[8], record_list[16], record_list[17], record_list[18],record_list[19]]
		print(battle_list)
		method = 'manual'
		self.delete_index.append(row)
		
		confirm_dialog = ConfirmDialog()
		self.signal_setbattlelist.emit(battle_list,self.fname,method)
		if confirm_dialog.exec() == QDialog.Accepted:
			pass
		
	def on_button_clicked(self, event):
		sender = self.sender()
		row = sender.property('row')
		column = sender.property('column')
		index = self.model.index(row, column, QModelIndex())
		sender.setEnabled(False)
		sender.setText('待删除')
		self.delete_index.append(row)
		
	def delete_row(self):
		df = pd.read_csv(self.fname)
		print('Delete: ')
		print(self.delete_index)	
		df.drop(self.delete_index,inplace=True)
		df.to_csv(self.fname,index=False,encoding="utf-8")
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/delete.png")
		painter.drawPixmap(self.rect(), pixmap)
		
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
		self.label1.setText("本软件遵循GPL开源协议\n开发作者：苦艾煎茶\n问题反馈群945558059")
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
		pixmap = QPixmap("./data/images/about.png")
		painter.drawPixmap(self.rect(), pixmap)

class BulkOKDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()
		
	def initUI(self):
		self.setWindowTitle('批量导入完成')
		self.setFixedSize(550, 200)
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
		self.label1 = QLabel()
		self.label1.setText("导入成功")
		self.label1.setAlignment(Qt.AlignCenter)
		self.label1.setStyleSheet("font-weight:bold;font-size:20px")	

		self.btnOk = QPushButton('OK',self)
		self.btnOk.clicked.connect(self.close)
		
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.btnOk)
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.label1)
		vbox.addLayout(hbox)
		
		self.setLayout(vbox)
		self.show()
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/bulkresult.png")
		painter.drawPixmap(self.rect(), pixmap)
		
class BulkLogDialog(QDialog):
	def __init__(self):
		super().__init__()
		window.signal_bulklog.connect(self.get_logs)
		self.initUI()
		self.show()
		
	def initUI(self):
		self.setWindowTitle('批量导入完成')
		self.setFixedSize(550, 200)
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		
		self.label1 = QLabel()
		self.label1.setText("导入完成，以下图片导入失败：")
		self.label1.setAlignment(Qt.AlignRight)
		self.label1.setStyleSheet("font-weight:bold;font-size:20px")
		
		self.btnOk = QPushButton('OK',self)
		self.btnOk.clicked.connect(self.close)
		
	def get_logs(self, logs):
		print('get logs:')
		print(logs)	
		self.content = QTextBrowser()
		self.content.setReadOnly(True)
		self.content.setOpenLinks(True)
		self.content.setOpenExternalLinks(True)
		self.content.setStyleSheet("background-color : rgba(255, 255, 255, 50)")
		
		logs_length = len(logs)
		for num in range(0,logs_length):
			template_string_data = '''
			<table border="0" align="center" style="background-color: rgba(255, 255, 255, 0.5);" >
				<tr>
					<th>{{ Link }}</th>
				</tr>
			'''
			template_data = Template(template_string_data)		
			html_data = template_data.render(
				Link = '<a href="' + str(logs[num]) + '">' + str(logs[num]) +'</a>'
			)
			self.content.append(html_data)
		
		hbox1 = QHBoxLayout()
		hbox1.addStretch(0.1)
		hbox1.addWidget(self.content)
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.btnOk)	

		vbox = QVBoxLayout()
		vbox.addWidget(self.label1)
		vbox.addLayout(hbox1)
		vbox.addLayout(hbox)
		
		self.setLayout(vbox)
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./data/images/bulkresult.png")
		painter.drawPixmap(self.rect(), pixmap)
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	apply_stylesheet(app, theme= './data/light_cyan_501.xml') 
	app.setWindowIcon(QIcon("./data/images/icon.ico"))
	app.setAttribute(Qt.AA_UseHighDpiPixmaps)
	window = MainWindow()
	sys.exit(app.exec())