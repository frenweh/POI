#coding=utf-8
# 爬取百度地图上的美食poi
#from selenium import webdriver 
#from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.action_chains import ActionChains
import util
import file_func
import psutil
import time
import sys    
from bs4 import BeautifulSoup
import re
import parseAddr

def addInfo(node,info):
	if len(node) > 0:
		info.append(node[0].get_text().strip())
	else:
		info.append(" ")

def parsePOI_Info(pageSource):
	soup = BeautifulSoup(pageSource,"lxml",from_encoding = "utf-8")
	poi_info = []
	uid = ""
	pattern_space = re.compile('[ ]+')
	pattern_num = re.compile(r'[\d%]+')

	nodes = soup.select('div[class="ml_30 mr_85"]')
	if len(nodes) > 0:
		name = nodes[0].select('div[class="row"] > span > a')
		addInfo(name,poi_info)

		label = nodes[0].select('div[class="row"]')
		if len(label) > 1:
			label = label[1].get_text().strip()
			label = re.sub(pattern_space, '', label)
			if "|" in label:
				tmp = label.split("|")
				if len(tmp) > 1:
					poi_info.append(tmp[0])
			else:
				poi_info.append(label)
				# poi_info.append(pattern_num.findall(tmp[1])[0])
		
		addr = nodes[0].select('div[class="row addr"] > span[class="n-grey"]')
		addInfo(addr,poi_info)

	nodes = soup.select('div[class="l-row"]')
	
	if len(nodes) > 0:
		aNode = nodes[0].select('span[class="operate ml_5"] > a')
		if len(aNode) > 2:
			href = aNode[2].get("href")
			tmp = href.split("&")
			for j in range(len(tmp)):
				if "lat=" in tmp[j]:
					lat = pattern_num.findall(tmp[j])[0]
					lat = round(float(lat)/100000,6)
					lat = '{:.6f}'.format(lat)
					poi_info.append(str(lat))
				elif "lng=" in tmp[j]:
					lng = pattern_num.findall(tmp[j])[0]
					lng = round(float(lng)/100000,6)
					lng = '{:.6f}'.format(lng)
					poi_info.append(str(lng))
				elif "uid=" in tmp[j]:
					uid = tmp[j].split('=')[1]
					poi_info.insert(0,uid)
	return uid,poi_info

def goToNextPage(broswer):
	nextPage = broswer.find_elements_by_css_selector("a[tid=\"toNextPage\"]")
	if len(nextPage) == 0:
		return False
	else:
		prePage = int(broswer.find_elements_by_css_selector("span[class=\"curPage\"]")[0].get_attribute('innerHTML'))
		nextPage[0].click()
		time.sleep(3)
		if len(broswer.find_elements_by_css_selector("span[class=\"curPage\"]")) == 0:
			return False
		curPage = int(broswer.find_elements_by_css_selector("span[class=\"curPage\"]")[0].get_attribute('innerHTML'))
		if prePage == curPage:
			return False
		time.sleep(6)
		# nextPage = broswer.find_elements_by_css_selector("a[tid=\"toNextPage\"]")
		# ActionChains(broswer).move_to_element(nextPage[0]).perform()
		return True

def chooseArea(broswer,area,type_):
	time.sleep(2)
	areaElement = util.findElementsByCssSelector(broswer,"li[data-type=\"city-panel\"]",False)
	time.sleep(1)
	areaElement.click()
	time.sleep(1)
	util.switchToCurrentWindow(broswer)
	ulElement = util.findElementsByClassName(broswer,"hd-list-wrap",False)
	time.sleep(1)
	# li = util.findElementsByLinkText(ulElement,area,False)
	# time.sleep(1)
	# li.click()
	# time.sleep(1)
	areaElement = util.findElementsByCssSelector(ulElement,'li[data-value="' + area + '"]',False)
	time.sleep(1)
	ActionChains(broswer).move_to_element(areaElement).perform()
	time.sleep(1)

	# lis = ulElement.find_elements_by_tag_name("li")
	# for li in lis:
	# 	if area in util.getInnerHtml(li).encode("utf-8"):
	# 		time.sleep(1)
	# 		ActionChains(broswer).move_to_element(li).perform()
	# 		time.sleep(1)
	# 		break
	bsAreaList = util.findElementById(broswer,"bsAreaList")
	areaAll = util.findElementsByLinkText(bsAreaList,type_,False)
	areaAll.click()
	time.sleep(1)

def chooseType(broswer,tag,type_):
	util.switchToCurrentWindow(broswer)
	time.sleep(1)
	areaElement = util.findElementsByCssSelector(broswer,"li[data-type=\"tag-panel\"]",False)
	time.sleep(2)
	areaElement.click()
	time.sleep(1)
	util.switchToCurrentWindow(broswer)
	divElement = util.findElementsByClassName(broswer,"cater-filter-tag",False)
	items = divElement.find_elements_by_tag_name("dl")
	for item in items:
		dt = item.find_elements_by_tag_name("dt")
		if len(dt) > 0:
			if tag in util.getInnerHtml(dt[0]).encode("utf-8"):
				print ("find tag")
				dd = item.find_elements_by_tag_name("dd")
				if "全部" in util.getInnerHtml(dd[0]).encode("utf-8"):
					li = dd[0].find_elements_by_tag_name("li")[0]
					li.find_elements_by_tag_name("a")[0].click()
				else:
					lis = dd[0].find_elements_by_tag_name("li")
					for li in lis:
						if type_ in util.getInnerHtml(li).encode("utf-8"):
							li.find_elements_by_tag_name("a")[0].click()
							break
				break
	time.sleep(1)

def chooseOrder(broswer,sortType):
	# sortType ["data_type,0","overall_rating,0","hot_value,0","price,0","price,1"]
	time.sleep(1)
	areaElement = util.findElementsByCssSelector(broswer,"li[data-type=\"sort-panel\"]",False)
	time.sleep(2)
	areaElement.click()
	time.sleep(1)
	sortElement = util.findElementById(broswer,"select_panel_sort")
	liElement = util.findElementsByCssSelector(sortElement,'a[data-value="sort:' + sortType + '"]',False)
	time.sleep(1)
	ActionChains(broswer).move_to_element(liElement).perform()
	liElement.click()
	time.sleep(4)

def getReady():
	# driverType = "phantomjs.exe"
	driverType = "geckodriver.exe"
	# driverType = "chromedriver.exe"
	running_pids1 = psutil.pids()
	broswer = util.createBrowser("https://map.baidu.com/")
	time.sleep(3)
	running_pids2 = psutil.pids()
	pid = util.getPid(running_pids1,running_pids2,driverType)
	util.switchToCurrentWindow(broswer)
	inputElement = util.findElementById(broswer,"sole-input")
	inputElement.clear()
	inputElement.send_keys(cityName.decode("utf-8"))#.decode("utf-8")
	searchBtn = util.findElementById(broswer,"search-button")
	searchBtn.click()
	time.sleep(2)
	inputElement.clear()
	inputElement.click()
	caterElement = util.findElementsByClassName(broswer,"city-special-item")
	caterElement = caterElement[0]
	caterElement.click()
	return pid,broswer

def gotoQuery(broswer):
	searchBtn = util.findElementById(broswer,"search-button")
	searchBtn.click()
	time.sleep(5)
def queryByInput(broswer,area,tag):
	inputElement = util.findElementById(broswer,"sole-input")
	time.sleep(3)
	inputElement.send_keys(" " + area.decode("utf-8") + " " + tag.decode("utf-8"))#.decode("utf-8")
	time.sleep(1)
	# inputElement.send_keys(" " + tag.decode("utf-8"))#.decode("utf-8")
	time.sleep(3)
	gotoQuery(broswer)
	element = util.findElementById(broswer,"cards-level1")
	ActionChains(broswer).move_to_element(element).perform()
	time.sleep(2)

def queryByChooseLabel(broswer,area,area_type,tag,tag_type):
	chooseArea(broswer,area,area_type)
	time.sleep(2)
	element = util.findElementById(broswer,"cards-level1")
	ActionChains(broswer).move_to_element(element).perform()
	time.sleep(3)
	chooseType(broswer,tag,tag_type)
	ActionChains(broswer).move_to_element(element).perform()
	time.sleep(3)

def getItemCount(broswer):
	poiElement = util.findElementsByClassName(broswer,"poilist")[0]
	pageSource = util.getInnerHtml(poiElement)
	soup = BeautifulSoup(pageSource,"lxml",from_encoding = "utf-8")
	lis = soup.select("li")
	return len(lis)

def main(cityName,area,area_type,tag,tag_type):
	pid = None
	broswer = None
	try:
		pid,broswer = getReady()

		# queryByChooseLabel(broswer,area,area_type,tag,tag_type)

		queryByInput(broswer,area,tag)

		hasNext = True
		i = 1
		while hasNext:
			print i
			i += 1
			if i >= 60:
				break
			poiElement = util.findElementsByClassName(broswer,"poilist")[0]
			items = poiElement.find_elements_by_tag_name("li")
			already_scraw = file_func.readFileToList("data/uid.txt")
			for item in items:
				pageSource = util.getInnerHtml(item)
				uid,poiInfo = parsePOI_Info(pageSource)
				if uid not in already_scraw:
					print uid + " not in"
					file_func.listAppendToTxt("data/info.txt",poiInfo)
					file_func.writeToTxt("data/uid.txt",uid)
				else:
					print uid + " in"
			time.sleep(1)
			hasNext = goToNextPage(broswer)
			# if len(util.findElementsByClassName(broswer,"no_result_title")) > 0:
			# 	gotoQuery(broswer)
			if getItemCount(broswer) == 0:
				gotoQuery(broswer)
			util.switchToCurrentWindow(broswer)
			time.sleep(2)
			cardElement = util.findElementById(broswer,"toast-wrapper")
			time.sleep(2)
			ActionChains(broswer).move_to_element(cardElement).perform()
			time.sleep(10)
			# poiElement = util.findElementsByClassName(broswer,"poilist")[0]
			# ActionChains(broswer).move_to_element(poiElement).perform()
		util.closeAllHandle(broswer)
		print pid
		util.terminatePid(pid)
	except Exception as e:
		print e
		util.closeAllHandle(broswer)
		print pid
		util.terminatePid(pid)
		# sys.exit()

def getAllArea(broswer):
	time.sleep(2)
	areaElement = util.findElementsByCssSelector(broswer,"li[data-type=\"city-panel\"]",False)
	time.sleep(1)
	areaElement.click()
	time.sleep(1)
	util.switchToCurrentWindow(broswer)
	ulElement = util.findElementsByClassName(broswer,"hd-list-wrap",False)
	time.sleep(1)
	lis = ulElement.find_elements_by_tag_name("li")
	result = {}
	for li in lis:
		time.sleep(1)
		ActionChains(broswer).move_to_element(li).perform()
		time.sleep(1)
		areaName = li.get_attribute("data-value")
		bsAreaList = util.findElementById(broswer,"bsAreaList")
		li_node = bsAreaList.find_elements_by_tag_name("li")
		result[areaName] = []
		for item in li_node:
			typeName = item.find_elements_by_tag_name("a")[0].get_attribute("innerHTML")
			result[areaName].append(typeName)
		print len(result[areaName])
	print len(result)
	return result

def getAllTag(broswer):
	util.switchToCurrentWindow(broswer)
	time.sleep(1)
	areaElement = util.findElementsByCssSelector(broswer,"li[data-type=\"tag-panel\"]",False)
	time.sleep(2)
	areaElement.click()
	time.sleep(1)
	util.switchToCurrentWindow(broswer)
	divElement = util.findElementsByClassName(broswer,"cater-filter-tag",False)
	items = divElement.find_elements_by_tag_name("dl")
	result = {}
	for item in items:
		dt = item.find_elements_by_tag_name("dt")
		if len(dt) > 0:
			tagName = dt[0].find_elements_by_tag_name("h2")[0].get_attribute("innerHTML").strip().encode("utf-8")
			dd = item.find_elements_by_tag_name("dd")
			lis = dd[0].find_elements_by_tag_name("li")
			result[tagName] = []
			for li in lis:
				tagType = li.find_elements_by_tag_name("a")[0].get_attribute("innerHTML").strip().encode("utf-8")
				result[tagName].append(tagType)
			print len(result[tagName])
	print len(result)
	time.sleep(1)
	
if __name__ == '__main__':
	cityName = "武汉市"
	city = "Wuhan"
	citycode = 218

	area = ["洪山区",'青山区','江岸区','武昌区','江汉区','汉阳区','硚口区'] # 补全
	# area = ["朝阳区","海淀区","丰台区","西城区","东城区","石景山区","昌平区","通州区","顺义区","房山区","门头沟区","大兴区","怀柔区","延庆区","平谷区","密云县"]
	area_type = ["全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部","全部"]
	tag = ['行政单位','政府机构','公司','企业','高校','工厂']
	tag_type = ["全部","全部","全部","全部","全部","全部"]

	# 1、生成所有待爬item
	tmp = file_func.readFileToList("data/" + city + "/item.txt")
	if len(tmp) == 0:
		for i in range(len(area)):
			for j in range(len(tag)):
				file_func.writeToTxt("data/" + city + "/item.txt",area[i] + "\t" + area_type[i] + "\t" + tag[j] + "\t" + tag_type[j])

	# #######################################################
	# 利用接口爬
	items = file_func.readFileToList("data/" + city + "/item.txt")
	for item in items:
		tmp = item.split("\t")
		# main(cityName,tmp[0],tmp[1],tmp[2],tmp[3])
		parseAddr.spiderByAPIMain("办公%20" + tmp[0] + "%20" + tmp[2], citycode, city)
		all_item = file_func.readFileToList("data/" + city + "/item.txt")
		del all_item[0]
		file_func.listWriteToTxt("data/" + city + "/item.txt",all_item)
		file_func.listWriteToTxt("data/" + city + "/cur_i.txt",["0"])
	# 	sys.exit()



	# ###################################################
	# 利用selenium爬取
	# broswer = getReady()
	# area = getAllArea(broswer)
	# tag = getAllTag(broswer)
	# util.closeAllHandle(broswer)
	# print pid
	# util.terminatePid(pid)

	# main(cityName,"海淀区","全部","西餐厅","全部")

	# http://api.map.baidu.com/geocoder/v2/?ak=l1efF5xp00r6mHIeesGh5amG&output=json&address=北京市石景山区古城大街19号

	# http://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=朝阳区&c=131&pn=1

	# https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=美食 朝阳区 中餐馆&c=131&src=0&wd2=&pn=0