#coding=utf-8
import os

def writeToTxt(fileUrl,url,something = None):
	f = open(fileUrl,'a')
	if something:
		f.write('%s\t%s\n' %(str(url),str(something)))
	else:
		f.write('%s\n' %(str(url)))
	f.close()
def readFile(fileUrl,poi):
    if os.path.isfile(fileUrl):
        f = open(fileUrl,"r")
        lines = f.readlines()
        proxys = []
        for line in lines:
            line = line.replace('\n', '')
            tmp = line.split("\t")
            info = ""
            poi.sort()
            for p in poi:
                info += tmp[p] + '\t'
            proxys.append(info)
        return proxys
    else:
        return []
def readFileToList(fileUrl):
    if os.path.isfile(fileUrl):
        f = open(fileUrl,"r")
        lines = f.readlines()
        proxys = []
        for line in lines:
            proxys.append(line.replace('\n', ''))
        return proxys 
    return []
def readFileToDict(fileUrl):
    if os.path.isfile(fileUrl):
        f = open(fileUrl,"r")
        lines = f.readlines()
        dicts = {}
        for line in lines:
            tmp = line.replace('\n', '').split("\t")
            dicts[tmp[0]] = int(tmp[1])
        return dicts
    else:
        return {}
def readFileToSet(fileUrl):
    if os.path.isfile(fileUrl):
        f = open(fileUrl,"r")
        lines = f.readlines()
        proxys = set()
        for line in lines:
            proxys.add(line.replace('\n', ''))
        return proxys
    else:
        return set()
def listWriteToTxt(fileUrl,info):
    f = open(fileUrl,'w')
    for item in info:
        f.write('%s\n' %(str(item)))
    f.close()
def listAppendToTxt(fileUrl,info,encoding = True):
    with open(fileUrl, "a") as fd:
        txt = "\t".join(info)
        if encoding:
            txt = txt.encode("utf-8")
        fd.write(txt)
        fd.write("\n")
def DictWriteToFile(fileUrl,dicts):
    f = open(fileUrl,'w')
    for (k, v) in dicts.items():
        f.write('%s\t%s\n' %(str(k),str(v)))
    f.close()

def readFileToStr(fileUrl):
    if os.path.isfile(fileUrl):
        f = open(fileUrl,"r")
        lines = f.readlines()
        proxys = []
        for line in lines:
            line = line.replace('\n', '').replace('\t', '')
            proxys.append(line)
        return "".join(proxys)
    return ""

def strWriteToTxt(fileUrl,str_):
    f = open(fileUrl,'w')
    f.write('%s\n' %(str(str_)))
    f.close()


# f = open("a.txt")
# line = f.readline().decode("gbk",'ignore')
# print(type(line))