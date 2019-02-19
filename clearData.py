#coding=utf-8
# 解析地址to经纬度

import urllib2
import json
import file_func
import os
import time
import re
import sys

def urlRequest(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	print response.getcode()
	if response.getcode()!=200:
		return None
	return response.read()

def readFileToDict(fileUrl):
	if os.path.isfile(fileUrl):
		f = open(fileUrl,"r")
		lines = f.readlines()
		dicts = {}
		for line in lines:
			# line = line.decode("gbk").encode("utf-8")
			tmp = line.replace('\n', '').split("\t")
			if tmp[-1] != "null":
				dicts[tmp[0]] = "\t".join(tmp[1:])
		return dicts
	else:
		return {}

def spiderPOIByAPI(keyword,citycode,pageCount = 0):
	# https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=美食 朝阳区 中餐馆&c=131&src=0&wd2=&pn=0
	url = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=" + keyword + "&c=" + str(citycode) + "&src=0&wd2=&pn=" + str(pageCount)
	print url
	html = urlRequest(url)
	if html is None:
		return {}
	result = {}
	try:
		result = json.loads(html)
	except Exception as e:
		print e
	# result = eval(html)
	print "load json"
	return result

def addInfo(info,label,jsonObj):
	if label in jsonObj:
		info.append(jsonObj[label])
	else:
		info.append(" ")

def parseJsonResult(result):
	print "start parse json"
	poiInfo = []
	if "content" not in result:
		return poiInfo
	content = result["content"]
	count = 0
	for i in range(len(content)):
		poi = []
		poi.append(content[i]["uid"] + "#1")
		poi.append(content[i]["name"])
		poi.append(content[i]["addr"])
		poi.append(str(content[i]["diPointX"]))
		poi.append(str(content[i]["diPointY"]))
		if 'std_tag' in content[i]:
			poi.append(content[i]['std_tag'])
		else:
			print 'not have std_tag'
			poi.append('')
		if "tel" in content[i]:
			poi.append(content[i]["tel"])
		else:
			print "not have tel"
			poi.append(" ")
		if len(content[i]["cla"]) == 1:
			poi.append(content[i]["cla"][0][1])#label
		else:
			poi.append(" ")
		addInfo(poi,"overall_rating",content[i]["ext"]["detail_info"])#rate
		addInfo(poi,"shop_hours",content[i]["ext"]["detail_info"])#营业时间
		addInfo(poi,"tag",content[i]["ext"]["detail_info"])#tag
		poiInfo.append(poi)
		if count >= 10:
			break
	return poiInfo

def spiderByAPIMain(keyword,citycode):
	page = file_func.readFileToList("data/cur_i.txt")
	cur_i = int(page[0])
	for i in range(cur_i,60):
		print i
		result = spiderPOIByAPI(keyword,citycode,i)
		poiInfo = parseJsonResult(result)
		print "parse over"
		if len(poiInfo) == 0:
			break
		already_scraw = file_func.readFileToList("data/uid.txt")
		already_scraw1 = file_func.readFileToList("data/uid_all.txt")
		for item in poiInfo:
			if item[0] not in already_scraw:
				print item[0] + " not in"
				file_func.writeToTxt("data/uid.txt",item[0])
				file_func.listAppendToTxt("data/info.txt",item[0:6])#
			else:
				print item[0] + " in"
			if item[0] not in already_scraw1:
				file_func.writeToTxt("data/uid_all.txt",item[0])
				file_func.listAppendToTxt("data/info_all.txt",item)
		file_func.listWriteToTxt("data/cur_i.txt",[i])
		time.sleep(10)

def addrToLatLnt(addr):
	aks = ["1c4c84e6462fecb243831130f9db4098","RquoEX471C87SGjM3kAkDLPX","s4p7FEHx8wYuMkha24BzwWBX","CA4de4f8d8e3c3891eb39a78f8343cd4","457568d0dbd40f01bbeb6814389edc8e","Y1kG709UBP4L0ac6SvTjxnm7","WUPGAouSp0YkG7yA6upSBlnL","GANo2ajua2rTiTTc05oKIrYr","3a345e5b8b56a7f80605cd95d64634a8","dASz7ubuSpHidP1oQWKuAK3q","0E9a1d87c1b0c5025565a115e62c8b90","0BnmmjUc3oredzfcbsZTG0Zh","Tg7cjyoPXqqliG19hIohzDWK","l1efF5xp00r6mHIeesGh5amG","CG8eakl6UTlEb1OakeWYvofh"]
	# addr = "北京市石景山区古城大街19号"
	for ak in aks:
		url = "http://api.map.baidu.com/geocoder/v2/?ak="+ ak +"&output=json&address=" + addr
		print(url)
		html = urlRequest(url)
		result = {}
		try:
			result = json.loads(html)
			file_func.strWriteToTxt("a.txt",html)
			print result
		except Exception as e:
			print e
		if len(result) > 0:
			if result["status"] == 0:
				break
		# break
	return result

def parseLatLnt(result):
	lat = lng = " "
	if "result" in result:
		if "location" in result["result"]:
			lat = result["result"]["location"]["lat"]
			lng = result["result"]["location"]["lng"]
	return lat,lng
	
def addToInfoP(lists):
	infoP = readFileToDict("data/info_p.txt")
	print len(infoP)
	for item in lists:
		tmp = item.split("\t")
		if tmp[0] not in infoP:
			file_func.listAppendToTxt("data/info_p.txt",tmp,False)
			infoP[tmp[0]] = "\t".join(tmp[1:])

def parseLatLngAndAddToInfoP(city):
	infoP = readFileToDict("data/" + city + "/info_p.txt")
	lists = file_func.readFileToList("data/" + city + "/info.txt")
	a1 = re.compile('\(.*\)')
	for item in lists:
		tmp = item.split("\t")
		if tmp[0] not in infoP:
			print tmp[2]
			addr = tmp[2]
			addr = addr.replace(" ","")
			if "武汉市" not in addr:
				addr = "武汉市" + addr
			if "、" in addr:
				addr = addr.split("、")
				addr = addr[0]
			if ";" in addr:
				addr = addr.split(";")
				addr = addr[0]
			addr = a1.sub('',addr)
			# print addr
			# sys.exit()
			result = addrToLatLnt(addr)
			if result["status"] == 2:
				file_func.listAppendToTxt("data/" + city + "/error_uid.txt",[tmp[0]])
			lat,lng = parseLatLnt(result)
			if lat != " ":
				tmp.append(str(lat))
				tmp.append(str(lng))
				file_func.listAppendToTxt("data/" + city + "/info_p.txt",tmp,False)
				infoP[tmp[0]] = "\t".join(tmp[1:])
			else:
				file_func.listAppendToTxt("data/" + city + "/error_uid.txt",[tmp[0]])

'''addr = "湖北省武汉市洪山区珞喻路4号"
a1 = re.compile('\(.*\)')
addr = a1.sub('',addr)
print addr'''
result=parseLatLngAndAddToInfoP('Wuhan')
'''
#result = addrToLatLnt(addr)
lat,lng = parseLatLnt(result)
print lat,lng

spiderByAPIMain("购物%20洪山区%20商场",218)

fileUrl = "test.txt"
content = file_func.readFileToStr("test.txt")
print json.loads(content)

dicts1 = readFileToDict("data/restaurant1.txt")
print len(dicts1)
dicts2 = readFileToDict("data/restaurant.txt")
print len(dicts2)
z = dict(dicts1, **dicts2)
print len(z)
file_func.DictWriteToFile("data/info1.txt",dicts2)

lists = []
uids = []
items = file_func.readFileToList("data/info1.txt")
for item in items:
    tmp = item.strip().split("\t")
    if len(tmp) == 8:
 		lists.append(item)
 		uids.append(tmp[0])
print len(uids)
file_func.listWriteToTxt("data/info1.txt",lists)
file_func.listWriteToTxt("data/uid.txt",uids)

lists = file_func.readFileToList("data/info1.txt")
addToInfoP(lists)
addToInfoP([])
'''