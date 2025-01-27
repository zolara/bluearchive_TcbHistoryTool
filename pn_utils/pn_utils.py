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
	
def code_to_sc(stud):
	if stud != '':
		stud_dict = pd.read_json('./data/studstr_sc2code.json', typ='series')
		for key, value in stud_dict.items():
			if value == stud:
				return key
		return '1NoData'
	else:
		return '1NoData'
	
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
		stud_dict = pd.read_json('./data/stuid.json', typ='series')
		for key, value in stud_dict.items():
			if value == stud:
				return key
		return ''
	else:
		return ''
		
def id_to_sc(stud):
	stud_dict = pd.read_json('./data/stuid.json', typ='series')
	try:
		return stud_dict[stud]
	except:
		return ''