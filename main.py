import sys
import os
import platform
import cv2
import datetime
import numpy as np
import csv
from string import punctuation
from paddleocr import PPStructure,draw_structure_result,save_structure_res
import pandas as pd
from jinja2 import Template

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from qt_material import apply_stylesheet

import studstr_sc2code
import studstr_scocr2sc

url = os.path.dirname(os.path.abspath(__file__))
os.environ["QT_FONT_DPI"] = "96"

widgets = None

class MainWindow(QWidget):
	signal_setbattlelist = Signal(list,str)
    
	def __init__(self):
		super().__init__()
		self.fname = ''
		self.picname = ''
		self.userid =''
		self.initUI()


	def initUI(self):
	
		#self.setWindowFlags(Qt.FramelessWindowHint)
		self.setFixedSize(1280, 720)  
		self.setWindowTitle('普拉娜的笔记本')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
		self.setAcceptDrops(True)			
		
		self.btnLoad = QPushButton('查看记录',self)
		self.btnSave = QPushButton('保存记录',self)
		self.btnSearch = QPushButton('查询用户历史阵容',self)
		self.btnAbout = QPushButton('关于',self)
		self.content = QTextEdit()
		
		grid = QGridLayout()
		self.setLayout(grid)
		
		grid.addWidget(self.btnLoad,1,1,1,1)
		grid.addWidget(self.btnSave,2,1,1,1)
		grid.addWidget(self.btnSearch,3,1,1,1)
		grid.addWidget(self.btnAbout,5,1,1,1)
		grid.addWidget(self.content,1,2,5,2)
		
		self.btnLoad.setStyleSheet("background-color : rgba(0, 0, 0, 30)")
		self.btnSave.setStyleSheet("background-color : rgba(0, 0, 0, 30)")
		self.btnAbout.setStyleSheet("background-color : rgba(0, 0, 0, 30)")
		self.content.setStyleSheet("background-color : rgba(0, 0, 0, 30)")
		
		self.btnLoad.clicked.connect(self.read_csv)
		self.btnSearch.clicked.connect(self.user_search)
		self.btnSave.clicked.connect(self.add_btnrecord)
	
		self.show()
		
	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls:
			if self.fname == '':
				event.ignore()
				the_dialog = NoCsvOpenDialog()
				if the_dialog.exec() == NoCsvOpenDialog.Accepted:
					pass
			else:
				self.picname = event.mimeData().text()[8:]
				self.add_newrecord(self)
				print(event.mimeData().text())
				event.accept()
		else:
			event.ignore()


	def add_newrecord(self, event):
		img_path = self.picname
		file_path = str(self.fname[0])		
		self.picname = ''
		
		self.ocr(file_path, img_path)

		
	def add_btnrecord(self, event):
		if self.fname == '':
			event.ignore()
			the_dialog = NoCsvOpenDialog()
			if the_dialog.exec() == NoCsvOpenDialog.Accepted:
				pass
		else:	
			img_name = QFileDialog.getOpenFileName(self, '选择截图', '.', '*.png')
			img_path = img_name[0]
			file_path = str(self.fname[0])
			
			self.ocr(file_path, img_path)
			
			
	def ocr(self, file_path, img_path):
		print('record: ' + file_path)
		print('img: ' + img_path)
		
		table_engine = PPStructure(show_log=True, table=True, image_orientation=False,)
					
		img = cv2.imread(img_path)
		cv2.rectangle(img, (1800,790),(1000,870),(216,225,256), -1)
		#cv2.rectangle(img, (1470,310),(1840,360),(216,225,256), -1)		
		#cv2.imshow("image", img)
		#cv2.waitKey(0)
		
		img1 = img[870:900,1000:1800]
		result1 = table_engine(img1)
		res0 = str(result1[0]['res'][0]['text'])
		new_res0 = ''.join(i for i in res0 if i.isalnum())
		res1 = str(result1[0]['res'][1]['text'])
		new_res1 = ''.join(i for i in res1 if i.isalnum())
		res2 = str(result1[0]['res'][2]['text'])
		new_res2 = ''.join(i for i in res2 if i.isalnum())
		res3 = str(result1[0]['res'][3]['text'])
		new_res3 = ''.join(i for i in res3 if i.isalnum())
		res4 = str(result1[0]['res'][4]['text'])
		new_res4 = ''.join(i for i in res4 if i.isalnum())
		res5 = str(result1[0]['res'][5]['text'])
		new_res5 = ''.join(i for i in res5 if i.isalnum())
		
		print(new_res0 + new_res1 + new_res2 + new_res3 + new_res4 + new_res5)
		
		img2 = img[250:370,1290:1860]
		result2 = table_engine(img2)
		#print(result2)
		res6 = str(result2[0]['res'][1]['text'])
		new_res6 = ''.join(i for i in res6 if i.isalnum())
		print(new_res6)

		w_res0 = self.scocr_to_sc(new_res0)
		w_res1 = self.scocr_to_sc(new_res1)
		w_res2 = self.scocr_to_sc(new_res2)
		w_res3 = self.scocr_to_sc(new_res3)
		w_res4 = self.scocr_to_sc(new_res4)
		w_res5 = self.scocr_to_sc(new_res5)
			
		battle_list = [new_res6, w_res0, w_res1, w_res2, w_res3, w_res4, w_res5]
		
		confirm_dialog = ConfirmDialog()
		self.signal_setbattlelist.emit(battle_list,file_path)
		if confirm_dialog.exec() == QDialog.Accepted:
			pass
			
	def read_csv(self, event):
		self.fname = QFileDialog.getOpenFileName(self, '选择csv记录', '.', '*.csv')
		print(self.fname)
		df = pd.read_csv(self.fname[0])	
		self.content.clear()
		df_img = df
		
		
		df_length = len(df_img)
		for num in range(0,df_length):
			template_string_data = '''
			<table border="1" align="right" style="background-color: rgba(255, 255, 255, 0.5);" >
				<tr>
					<th>{{ UserId }}</th>
					<th>{{ Date }}</th>
					<th>{{ Attacker1 }}</th>
					<th>{{ Attacker2 }}</th>
					<th>{{ Attacker3 }}</th>
					<th>{{ Attacker4 }}</th>
					<th>{{ Special1 }}</th>
					<th>{{ Special2 }}</th>
					<th>{{ Formation }}</th>
				</tr>
			'''
			template_data = Template(template_string_data)
			html_data = template_data.render(
				UserId = '<br><br>' + str(df_img.iloc[num,0]),
				Date = '<br><br>' + str(df_img.iloc[num,1]),
				Attacker1 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,2] + '.png width=90/>',
				Attacker2 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,3] + '.png width=90/>',
				Attacker3 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,4] + '.png width=90/>',
				Attacker4 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,5] + '.png width=90/>',
				Special1 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,6] + '.png width=90/>',
				Special2 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,7] + '.png width=90/>',
				Formation = '<br><br>' + str(df_img.iloc[num,8])
			)
			self.content.append(html_data)
			
	def user_search(self):
		search_dialog = SearchDialog()
		search_dialog.signal_setid.connect(self.get_id)
		if search_dialog.exec() == QDialog.Accepted:
			pass

	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./images/bg.jpg")
		painter.drawPixmap(self.rect(), pixmap)
		
	def resizeEvent(self, event):
		size = self.size()
		newheight = int(size.width() * 9/16)
		self.resize(size.width(), newheight)
		
	def get_id(self,userid):
		self.userid = userid
		print('get ' + self.userid)
		self.content.clear()
		self.content.append(userid)
		
		df = pd.read_csv(self.fname[0])	
		df_img = df[df['UserId'] == userid]
		print(df_img)
		
		
		
		df_length = len(df_img)
		for num in range(0,df_length):
			template_string_data = '''
			<table border="1" align="right">
				<tr>
					<th>{{ UserId }}</th>
					<th>{{ Date }}</th>
					<th>{{ Attacker1 }}</th>
					<th>{{ Attacker2 }}</th>
					<th>{{ Attacker3 }}</th>
					<th>{{ Attacker4 }}</th>
					<th>{{ Special1 }}</th>
					<th>{{ Special2 }}</th>
					<th>{{ Formation }}</th>
				</tr>
			'''
			template_data = Template(template_string_data)
			html_data = template_data.render(
				UserId = '<br><br>' + str(df_img.iloc[num,0]),
				Date = '<br><br>' + str(df_img.iloc[num,1]),
				Attacker1 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,2] + '.png width=90/>',
				Attacker2 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,3] + '.png width=90/>',
				Attacker3 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,4] + '.png width=90/>',
				Attacker4 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,5] + '.png width=90/>',
				Special1 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,6] + '.png width=90/>',
				Special2 = '<img src=' + url + '/images/stud/' + df_img.iloc[num,7] + '.png width=90/>',
				Formation = '<br><br>' + str(df_img.iloc[num,8])
			)
			self.content.append(html_data)
			
	def sc_to_code(self,stud):
		return studstr_sc2code.stud_dict[stud]
		
	def scocr_to_sc(self,stud):
		return studstr_scocr2sc.stud_dict[stud]

	
		
class ConfirmDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.file_name = ''
		window.signal_setbattlelist.connect(self.get_battlelist)
		
		
	def initUI(self):
		self.setFixedSize(600, 210)  
		self.setWindowTitle('确认数据')
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)
			
		self.labelUser = QLabel('对手ID', self)
		self.label1 = QLabel('突击①', self)
		self.label2 = QLabel('突击②', self)
		self.label3 = QLabel('突击③', self)
		self.label4 = QLabel('突击④', self)
		self.label5 = QLabel('支援①', self)
		self.label6 = QLabel('支援②', self)
		self.lineEditUser = QLineEdit()
		self.lineEdit1 = QLineEdit()
		self.lineEdit2 = QLineEdit()
		self.lineEdit3 = QLineEdit()
		self.lineEdit4 = QLineEdit()
		self.lineEdit5 = QLineEdit()
		self.lineEdit6 = QLineEdit()
		self.btnOk = QPushButton('OK',self)
		
		grid = QGridLayout()
		self.setLayout(grid)
		
		grid.addWidget(self.labelUser,1,1,1,1)
		grid.addWidget(self.label1,1,2,1,1)
		grid.addWidget(self.label2,1,3,1,1)
		grid.addWidget(self.label3,1,4,1,1)
		grid.addWidget(self.label4,1,5,1,1)
		grid.addWidget(self.label5,3,4,1,1)
		grid.addWidget(self.label6,3,5,1,1)
		self.labelUser.setAlignment(Qt.AlignCenter)
		self.label1.setAlignment(Qt.AlignCenter)
		self.label2.setAlignment(Qt.AlignCenter)
		self.label3.setAlignment(Qt.AlignCenter)
		self.label4.setAlignment(Qt.AlignCenter)
		self.label5.setAlignment(Qt.AlignCenter)
		self.label6.setAlignment(Qt.AlignCenter)
		self.labelUser.setStyleSheet("font-weight:bold;font-size:20px")
		self.label1.setStyleSheet("font-weight:bold;font-size:20px")
		self.label2.setStyleSheet("font-weight:bold;font-size:20px")
		self.label3.setStyleSheet("font-weight:bold;font-size:20px")
		self.label4.setStyleSheet("font-weight:bold;font-size:20px")
		self.label5.setStyleSheet("font-weight:bold;font-size:20px")
		self.label6.setStyleSheet("font-weight:bold;font-size:20px")
		
		grid.addWidget(self.lineEditUser,2,1,1,1)
		grid.addWidget(self.lineEdit1,2,2,1,1)
		grid.addWidget(self.lineEdit2,2,3,1,1)
		grid.addWidget(self.lineEdit3,2,4,1,1)
		grid.addWidget(self.lineEdit4,2,5,1,1)
		grid.addWidget(self.lineEdit5,4,4,1,1)
		grid.addWidget(self.lineEdit6,4,5,1,1)
		
		grid.addWidget(self.btnOk,5,5,1,1)		
		self.btnOk.setStyleSheet("background-color : rgba(176,196,222,1)")
		
		self.btnOk.clicked.connect(self.insert_table)
		self.btnOk.clicked.connect(self.close)
		
		self.show()
		
	def get_battlelist(self, battle_list, file_name):
		self.lineEditUser.setText(battle_list[0])
		self.lineEdit1.setText(battle_list[1])
		self.lineEdit2.setText(battle_list[2])
		self.lineEdit3.setText(battle_list[3])
		self.lineEdit4.setText(battle_list[4])
		self.lineEdit5.setText(battle_list[5])
		self.lineEdit6.setText(battle_list[6])
		self.file_path = file_name
		
	def sc_to_code(self,stud):
		return studstr_sc2code.stud_dict[stud]
		
	def scocr_to_sc(self,stud):
		return studstr_scocr2sc.stud_dict[stud]
		
	def insert_table(self, event):
		print('insert: ')
		
		userId = self.lineEditUser.text()
		atk1 = self.sc_to_code(self.lineEdit1.text())
		atk2 = self.sc_to_code(self.lineEdit2.text())
		atk3 = self.sc_to_code(self.lineEdit3.text())
		atk4 = self.sc_to_code(self.lineEdit4.text())
		spl1 = self.sc_to_code(self.lineEdit5.text())
		spl2 = self.sc_to_code(self.lineEdit6.text())
		
		print(userId,str(datetime.date.today()),atk1,atk2,atk3,atk4,spl1,spl2)
		
		with open(self.file_path, "a", encoding="utf-8", newline="") as f:
			wf = csv.writer(f)
			new_data = [userId,str(datetime.date.today()),atk1,atk2,atk3,atk4,spl1,spl2,'Defend']
			wf.writerow(new_data)
			f.close()
	
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./images/confirm.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	
			
class SearchDialog(QDialog):
	signal_setid = Signal(str)
	
	def __init__(self):
		super().__init__()
		self.initUI()
		
		
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
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./images/search.png")
		painter.drawPixmap(self.rect(), pixmap)
		
	def set_userid(self):
		userid = self.lineEdit.text()
		self.signal_setid.emit(userid)
		
		
class NoCsvOpenDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('没有被打开的记录文件')
		self.setFixedSize(400, 400)
		self.setWindowFlags(Qt.WindowCloseButtonHint & Qt.WindowMinimizeButtonHint)

		self.buttonclose = QPushButton('OK',self)
		self.buttonclose.clicked.connect(self.close)
		
		vbox = QVBoxLayout()
		vbox.addStretch(1)
		vbox.addWidget(self.buttonclose)
		self.setLayout(vbox)
		self.show()
		
	def paintEvent(self, event):		
		painter = QPainter(self)
		pixmap = QPixmap("./images/Nocsv.png")
		painter.drawPixmap(self.rect(), pixmap)
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	apply_stylesheet(app, theme= url+'/qt_material/themes/light_cyan_501.xml') 
	app.setWindowIcon(QIcon(url+"/images/icon.ico"))
	window = MainWindow()
	sys.exit(app.exec())