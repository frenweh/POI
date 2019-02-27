# POI
使用python爬取武汉市POI,并对结果进行坐标转化。由于课题组实验需要，对武汉市的美食，购物，住宅区的POI进行了爬取。实验主要运用Python的requests及BeautifuiSoup模块来完成。
网页爬虫本质可总结两步：
1、设置请求参数（url，headers，cookies，post或get验证等）访问目标站点的服务器；
2、解析服务器返回的文档，提取需要的信息。
而API的工作机制与爬虫的两步类似，但也有些许不同：API一般只需要设置url即可，且请求方式一般为“get”方式；API服务器返回的通常是json或xml格式的数据，解析更简单
这里主要利用城市内检索（对应JavaScriptAPI的Search方法）在指定区域检索POI服务。
在POI爬取结束后，由于爬取结果中的坐标为百度坐标，需要通过计算将其转换为WGS 84坐标。
