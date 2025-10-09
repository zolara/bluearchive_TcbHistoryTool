import pandas as pd

def get_aronatoken(key):
	json_dict = pd.read_json('./data/token.json', typ='series')
	return json_dict[key]

def get_query_tablename(key):
	json_dict = pd.read_json('./data/tablequery_map.json', typ='series')
	return json_dict[key]
	
def sc_to_code(stud):
	stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
	return stud_dict[stud]
	
def sc_to_code(stud, method):
	if method != 'manual':
		if stud != '':
			stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
			return stud_dict[stud]
		else:
			return '1NoData'
	else:
		if stud != '':
			stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
			return stud_dict[stud]
		else:
			return '1NoData'
	
def code_to_sc(stud):
	if stud != '':
		stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
		for key, value in stud_dict.items():
			if value == stud:
				return key
		return '1NoData'
	else:
		return ''
	
def nickname_to_code(stud):
	stud_dict = pd.read_json('./data/studstr_nickname2code.json', typ='series')
	try:
		stud_name = stud_dict[stud]
	except KeyError:
		stud_name = ''
	return stud_name

def scocr_to_sc(stud):
	stud_dict = pd.read_json('./data/studstr_scocr2sc.json', typ='series')
	try:
		stud_name = stud_dict[stud]
	except KeyError:
		stud_name = ''
	return stud_name
	
def tcocr_to_sc(stud):
	stud_dict = pd.read_json('./data/studstr_tcocr2sc.json', typ='series')
	try:
		stud_name = stud_dict[stud]
	except KeyError:
		stud_name = ''
	return stud_name

def jpocr_to_sc(stud):
	stud_dict = pd.read_json('./data/studstr_jpocr2sc.json', typ='series')
	try:
		stud_name = stud_dict[stud]
	except KeyError:
		stud_name = ''
	return stud_name

def sc_to_id(stud):
	if stud != '':
		try:
			stud_dict = pd.read_json('./data/stuid.json', typ='series')
			for key, value in stud_dict.items():
				if value == stud:
					return key
		except KeyError:
			return '1Nodata'
	else:
		return ''
		
def id_to_sc(stud):
	stud_dict = pd.read_json('./data/stuid.json', typ='series')
	try:
		stud_name = stud_dict[str(stud)]
	except:
		stud_name = '1Nodata'
	return stud_name

def isPixelValue(colorlist, B, G, R, allowance = 5):
	if colorlist[0] < B-allowance or colorlist[0] > B+allowance or colorlist[1] < G-allowance or colorlist[1] > G+allowance or colorlist[2] < R-allowance or colorlist[2] > R+allowance:
		print("不满足颜色容差。")
		return 1
	else:
		return 0
		
def isStandardResolution(height, width, img):
	img_height, img_width = img.shape[:2]
	if height != 1080:
		print("分辨率非法！")
		return 1
	if width != 1920:
		print("分辨率非法！")
		return 1
	return 0