# seleniumSpider

1.使用python+selenium+chromeDriver-headless爬取戊戌数据的药品说明。

2.功能介绍：

     ​	接收一组药品名称的输入，返回药品的名称、对应的生产公司、药品规格、适应症


3.文件结构介绍：

     ​	main.py为项目入口，接受一组药品名称，输出最终结果（linux和win的区别在于chrome驱动路径不同）
    
     ​	DIRVER为chrome浏览器驱动，使用本项目首先要安装chrome，下载chrome驱动并将驱动加入系统变量
    
     ​	getNameAndIndicationsFromHtml.py是匹配名称、公司、规格、适应症，最终结构化输出
    
     ​	ocr2jsonNanjing.py为南京ocr接口的项目调用
    
     ​	img2json.py为南京ocr接口模板（未使用）
    
     ​	ocr2jsonYoudao.py为网易有道ocr接口的项目调用（最终未使用）
    
     ​	spider_getDetails.py为爬取药品的详情页代码（最终未使用）
    
     ​	svg2html2img.py为是将药品网页中的某些svg字段转化为html并截图（最终已经集成到main中）
    
     ​	pages文件夹为爬取的网页结果,其中规格列和公司列为svg，因此需要将其转化为图片
    
     ​	pagesHtml为上面爬取网页结果的解析，将规格和公司提取出来组成新的页面，然后通过chrome截图保存
    
     ​	pagesImgs为截图结果示例
    
     ​	pagesJson为ocr解析截图的结果
    
     ​	result文件夹为excel结果
    
     ​	demo.xlsx为第一次爬取的最终结果展示
4.docker镜像:  https://hub.docker.com/repository/docker/gdzx/spider-wuxuwang_com