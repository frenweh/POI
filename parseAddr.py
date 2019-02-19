#coding=utf-8

import urllib2
import json
import file_func
import os
import time
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

def urlRequest(url):
	thePage = None
	while thePage is None:
		req = urllib2.Request(url)
		try:
			response = urllib2.urlopen(req,timeout = 10)
			print response.getcode()
			if response.getcode()!=200:
				return None
			time.sleep(1)
			thePage = response.read()
		except Exception as e:
			print e
			thePage = None
		print "read"
	return thePage

def readFileToDict(fileUrl):
	if os.path.isfile(fileUrl):
		f = open(fileUrl,"r")
		lines = f.readlines()
		dicts = {}
		for line in lines:
			line = line.decode("gbk")
			tmp = line.replace('\n', '').split("\t")
			if tmp[-1] != "null":
				dicts[tmp[0]] = "\t".join(tmp[1:])
		return dicts
	else:
		return {}

def spiderPOIByAPI(keyword,citycode,pageCount = 0):
	# https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=美食 朝阳区 中餐馆&c=131&src=0&wd2=&pn=0
	url = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=" + keyword + "&c=" + str(citycode) + "&src=0&wd2=&pn=" + str(pageCount)
	# url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd='+keyword+'&c='+ str(citycode) +'&src=0&wd2=&pn='+str(pageCount)+'&sug=0&l=13&from=webmap&biz_forward={"scaler":1,"styles":"pl"}&sug_forward=&auth=5w4Daw01yede=v9LGXIQ=6FDSDLCV4CCuxHEBLLLEVNtComRB199Ay1uVt1GgvPUDZYOYIZuxtEdwKv7ucvY1SGpuHt300b0z8yPWv3Guzt7xjhN@ThwzBDGJ4P6VWvcEWe1GD8zv7u@ZPuxtfvCu0iyfixA321NNN1NCwgjLLwzzvC00dE2&device_ratio=1&tn=B_NORMAL_MAP&nn=0&ie=utf-8&t=' + str(int(time.time()))
	print url
	html = urlRequest(url)
	if html is None:
		return {}
	result = {}
	file_func.strWriteToTxt("test.txt",html)
	print "write to txt"
	try:
		content = file_func.readFileToStr("test.txt")
		time.sleep(3)
		result = json.loads(content)
		time.sleep(3)
	except Exception as e:
		print e
	# result = eval(html)
	print "load json"
	return result

def addInfo(info,label,jsonObj):
	if label in jsonObj:
		if jsonObj[label] == "":
			info.append(" ")
		else:
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
		if "detail_info" in content[i]["ext"]:
			addInfo(poi,"overall_rating",content[i]["ext"]["detail_info"])#rate
			addInfo(poi,"shop_hours",content[i]["ext"]["detail_info"])#营业时间
			addInfo(poi,"tag",content[i]["ext"]["detail_info"])#tag
		else:
			poi.append(" ")
			poi.append(" ")
			poi.append(" ")
		poiInfo.append(poi)
		if count >= 10:
			break
	return poiInfo

def spiderByAPIMain(keyword,citycode,city):
	page = file_func.readFileToList("data/" + city + "/cur_i.txt")
	if len(page) == 0:
		page = [0]
	cur_i = int(page[0])
	for i in range(cur_i,60):
		print i
		result = spiderPOIByAPI(keyword,citycode,i)
		poiInfo = parseJsonResult(result)
		print "parse over"
		if len(poiInfo) == 0:
			print "break"
			break
		already_scraw = file_func.readFileToList("data/" + city + "/uid.txt")
		already_scraw1 = file_func.readFileToList("data/" + city + "/uid_all.txt")
		for item in poiInfo:
			if item[0] not in already_scraw:
				print item[0] + " not in"
				already_scraw.append(item[0])
				file_func.writeToTxt("data/" + city + "/uid.txt",item[0])
				file_func.listAppendToTxt("data/" + city + "/info.txt",item[0:6])#
			else:
				print item[0] + " in"
			if item[0] not in already_scraw1:
				file_func.writeToTxt("data/" + city + "/uid_all.txt",item[0])
				file_func.listAppendToTxt("data/" + city + "/info_all.txt",item)
		file_func.listWriteToTxt("data/" + city + "/cur_i.txt",[i])
		time.sleep(10)

def addrToLatLnt(addr):
	aks = ["Tg7cjyoPXqqliG19hIohzDWK","l1efF5xp00r6mHIeesGh5amG","CG8eakl6UTlEb1OakeWYvofh"]
	addr = "北京市石景山区古城大街19号"
	for ak in aks:
		url = "http://api.map.baidu.com/geocoder/v2/?ak="+ ak +"&output=json&address=" + addr
		html = urlRequest(url)
		result = {}
		try:
			result = json.loads(html)
		except Exception as e:
			print e
		if len(result) > 0:
			if result["status"] != 302:
				break
	return result

def parseLatLnt(result):
	lat = lng = " "
	if "result" in result:
		if "location" in result["result"]:
			lat = result["result"]["location"]["lat"]
			lng = result["result"]["location"]["lng"]
	return lat,lng

# spiderByAPIMain("美食%20朝阳区%20中餐馆",131,"Wuhan")

# fileUrl = "test.txt"
# if os.path.isfile(fileUrl):
#     f = open(fileUrl,"r")
#     lines = f.readlines()
#     proxys = []
#     for line in lines:
#         line = line.replace('\n', '')
#         proxys.append(line)
#     print json.loads("".join(proxys))

# dicts1 = readFileToDict("data/restaurant1.txt")
# print len(dicts1)
# dicts2 = readFileToDict("data/restaurant2.txt")
# print len(dicts2)
# z = dict(dicts1, **dicts2)
# print len(z)
# file_func.DictWriteToFile("data/info1.txt",z)

# lists = []
# uids = []
# items = file_func.readFileToList("data/info2.txt")
# for item in items:
# 	tmp = item.strip().split("\t")
# 	if len(tmp) == 6:
# 		lists.append(item)
# 		uids.append(tmp[0])
# print len(uids)
# file_func.listWriteToTxt("data/info.txt",lists)
# file_func.listWriteToTxt("data/uid.txt",uids)


# addr = "北京市石景山区古城大街19号"
# url = "http://api.map.baidu.com/geocoder/v2/?ak=l1efF5xp00r6mHIeesGh5amG&output=json&address=" + addr
# html = urlRequest(url)
# print json.loads(html)
    







