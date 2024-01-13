from modules.xdbSearcher import XdbSearcher


# # 1. 预先加载整个 xdb
# dbPath = "../res/china.xdb"
# cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)
#
# # 2. 仅需要使用上面的全文件缓存创建查询对象, 不需要传源 xdb 文件
# searcher = XdbSearcher(contentBuff=cb)
#
# # 3. 执行查询
# ip = "112.90.154.222"
# region_str = searcher.search(ip)
# print(region_str)
#
# # 4. 关闭searcher
# searcher.close()


# 在程序启动时加载整个 xdb 文件到内存中
dbPath = "../res/china.xdb"
content_buff = XdbSearcher.loadContentFromFile(dbfile=dbPath)
searcher = XdbSearcher(contentBuff=content_buff)

def ip_search(ip):
    # 执行查询
    result = searcher.search(ip)
    # 提取需要的字段
    province = result.split('|')[2]
    city = result.split('|')[3]
    district = result.split('|')[4]
    isp = result.split('|')[-3]
    print(f"IP:{ip} 省: {province}, 市: {city}, 区: {district}, 运营商: {isp}")

# 示例查询
ip_search("218.61.165.128")

