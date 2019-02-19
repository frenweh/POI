#coding=utf-8
#from selenium import webdriver 
#from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.support.ui import WebDriverWait
import psutil

def closeAllHandle(browser):
	all_handles = browser.window_handles
	for i in range(len(all_handles) - 1,-1,-1):
		browser.switch_to_window(all_handles[int(i)])
		browser.close()

def switchToCurrentWindow(browser):
	all_handles = browser.window_handles
	browser.switch_to_window(all_handles[len(all_handles) - 1])#切换到当前窗口

def createBrowser(url):
	# browser = webdriver.PhantomJS()
	browser = webdriver.Firefox()
	# browser = webdriver.Chrome()
	# browser.set_page_load_timeout(10)
	# browser.set_script_timeout(10)
	# broswer.minimize_window()
	browser.implicitly_wait(30)
	try:
		browser.get(url)
	except:
		pass
	print "强制超时"
	return browser

def getPageSource(browser):
	all_handles = browser.window_handles
	browser.switch_to_window(all_handles[len(all_handles) - 1])
	pageSource = browser.page_source
	return pageSource

def getPid(pids1,pids2,pName):
	targetPid = None
	diff_list_pids = list(set(pids2).difference(set(pids1)))
	for pid in diff_list_pids:
		p = psutil.Process(pid)
		if p.name() == pName:
			targetPid = pid
	return targetPid

def terminatePid(pid):
	p = psutil.Process(pid)
	if p:
		print p.name() + " already terminated"
		p.terminate()

def findElementById(browser,id_):
	items = browser.find_elements_by_id(id_)
	if len(items) == 0:
		return None
	else:
		return items[0]

def findElementsByClassName(browser,className,isMulti = True):
	items = browser.find_elements_by_class_name(className)
	if len(items) == 0:
		return []
	else:
		if isMulti:
			return items
		else:
			return items[0]

def findElementsByLinkText(browser,linkText,isMulti = True):
	items = browser.find_elements_by_link_text(linkText)
	if len(items) == 0:
		return None
	else:
		if isMulti:
			return items
		else:
			return items[0]

def findElementsByCssSelector(broswer,css,isMulti = True):
	nextPage = broswer.find_elements_by_css_selector(css)
	if len(nextPage) == 0:
		return None
	else:
		if isMulti:
			return nextPage
		else:
			return nextPage[0]

def getInnerHtml(node):
	return node.get_attribute('innerHTML')