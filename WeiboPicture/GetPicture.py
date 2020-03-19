import requests
import threadpool as threadpool

class WbGrawler():
    def __init__(self):
        """
        参数的初始化
        :return: 
        """
        self.baseurl = "https://m.weibo.cn/api/container/getIndex?containerid=1076032240077631&"
        self.headers = {
            "Host": "m.weibo.cn",
            "Referer": "https://m.weibo.cn/p/1076032240077631",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "X-Requested-with": "XMLHttpRequest"
        }
        # 图片保存路径
        self.path = "E:/Sunnio_picture/"

    def getPageJson(self, page):
        """
        获取单个页面的json数据
        :param page:传入的page参数
        :return:返回页面响应的json数据
        """
        url = self.baseurl + "page=%d" % page
        try:
            response = requests.get(url, self.headers)
            if response.status_code == 200:
                return response.json()
        except requests.ConnectionError as e:
            print("error", e.args)

    def parserJson(self, json):
        """
        解析json数据得到目标数据
        :param json: 传入的json数据
        :return: 返回目标数据
        """
        items = json.get("data").get("cards")
        for item in items:
            pics = item.get("mblog").get("pics")
            picList = []
            # 有些微博没有配图，所以需要加一个判断，方便后面遍历不会出错
            if pics is not None:
                for pic in pics:
                    pic_dict = {}
                    pic_dict["pid"] = pic.get("pid")
                    pic_dict["url"] = pic.get("large").get("url")
                    pic_dict['time'] = item.get("mblog").get('created_at')
                    picList.append(pic_dict)
            yield picList

    def imgDownload(self, results):
        """
        下载图片
        :param results:
        :return:
        """
        for result in results:
            for img_dict in result:  # img_dict 相当于item
                img_name = img_dict.get('time') + img_dict.get("pid")[25:] + ".jpg" #timestr_standard(data['created_at']) + '_' + pid[25:]#构建保存图片文件名，timestr_standard是一个把微博的created_at字符串转换为‘XXXX-XX-XX’形式日期的一个函数
                try:
                    img_data = requests.get(img_dict.get("url")).content
                    with open(self.path + img_name, "wb") as file:
                        file.write(img_data)
                        file.close()
                        print(img_name + "\tdownload successed!")
                except Exception as e:
                    print(img_name + "\tdownload failed!", e.args)

    def startCrawler(self, page):
        page_json = self.getPageJson(page)
        results = self.parserJson(page_json)
        self.imgDownload(results)

if __name__ == '__main__':
    wg = WbGrawler()
    pool = threadpool.ThreadPool(10)
    reqs = threadpool.makeRequests(wg.startCrawler, range(2, 67))
    [pool.putRequest(req) for req in reqs]
    pool.wait()