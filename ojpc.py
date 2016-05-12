# coding = utf-8
import re
import requests
from bs4 import BeautifulSoup
import warnings
import os

indexUrl = "http://acm.bjfu.edu.cn/acmhome/welcome.do?method=index"
loginUrl = "http://acm.bjfu.edu.cn/acmhome/login.do"
contestUrl = "http://acm.bjfu.edu.cn/acmhome/showstatus.do?problemId=null&contestId=&userName=null&result=&language=&page="
warnings.filterwarnings("ignore")

loc = "/Users/leohujx/Documents/code_4"     # 存放所有代码的位置，要事先新建一个文件夹

class ojpc():
    def __init__(self, username, psw):      # 登陆系统获取cookie
        self.header = {
            'Host': 'acm.bjfu.edu.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://acm.bjfu.edu.cn/acmhome/welcome.do?method=index',
        }

        data = {
            'userName': username,
            'password': psw,
        }
        rq = requests.get(indexUrl, headers=self.header)
        self.cookies = rq.cookies
        rq = requests.post(loginUrl, data=data, headers=self.header, cookies=self.cookies)
        # print(rq.text)

    # def getLoc(self):
    #     cf = configparser.ConfigParser()
    #     cf.read('Init.ini', encoding='utf-8')
    #     return cf.get('codePath', 'path')

    def get_td_array(self, content):                # 筛选数据，将table提取出来，并且正则匹配所有代码链接
        content = re.sub("<table[^>]*?>", "", content, flags=re.DOTALL)
        content = re.sub("<tr[^>]*?>", "", content, flags=re.DOTALL)
        content = re.sub("<td[^>]*?>", "", content, flags=re.DOTALL)
        content = re.sub("<script[^>]*?>.*?</script>", "", content, flags=re.DOTALL)
        content = content.strip()
        content = re.sub("</tr>", "{tr}", content, flags=re.DOTALL)
        href = re.findall(r"<a\s*href=\"(/acmhome/solutionCode\.do\?id=\S*)\"[^>]*?>\S*</a>", content)  # 匹配所code链接
        content = re.sub("<[/!]*?[^<>]*?>", "", content, flags=re.DOTALL)
        content = re.sub("([rn])[s]+", "", content, flags=re.DOTALL)
        content = re.sub(" ", "", content, flags=re.DOTALL)
        content = re.sub(" ", "", content, flags=re.DOTALL)
        content = content.strip()
        content = content.split('{tr}')
        i = 0
        while i < len(content):
            content[i] = re.sub('[\r\n\t]', ' ', content[i])
            i += 1
        return content, href

    def getPages(self, totalSubmit):        # 得到比赛中一共有几个提交页面
        pagenum = totalSubmit // 20
        if totalSubmit % 20 != 0:
            pagenum += 1
        return pagenum

    def run(self, pagenum, url):            #
        # loc = self.getLoc()
        for page in range(1, pagenum + 1):
            print("正在处理第" + str(page) + "页......请稍后!")
            newurl = url + str(page)            # 拼接新的url
            rq = requests.get(newurl, headers=self.header, cookies=self.cookies)
            txt = rq.text
            # print(txt)
            content, href = self.get_td_array(txt)
            # print(content)
            len1 = len(content)
            x = -1
            y = -1
            for i in range(0, len1):
                content[i] = content[i].strip()
                content[i] = re.split(r"\s*", content[i])
                if "状态" in content[i][0] and "题目号:" in content[i][1] and x == -1:
                    x = i
                if "[上一页]" in content[i][0] and "[下一页]" in content[i][1] and y == -1:
                    y = i
            content = content[x + 1:y]      # 切割list,将提交的那部分数据提取出来
            len1 = y - (x + 1)
            for i in range(0, len1):
                try:
                    if "Accepted" in content[i][2]: # 如果该提交是ac的
                        acUrl = href[i]
                        acUrl = "http://acm.bjfu.edu.cn" + acUrl    # 获取该ac代码的链接
                        # print(acUrl)
                        rq = requests.get(acUrl, headers=self.header, cookies=self.cookies)
                        txt = rq.text
                        loc1 = os.path.join(loc, content[i][0])
                        if os.path.exists(loc1) is False:   # 检查该学号是否已经创建文件夹
                            os.mkdir(loc1)
                        loc2 = os.path.join(loc1, str(content[i][1]) + '.txt')
                        if os.path.isfile(loc2): # 检查该学号下的某道题目是不是已经做了，这样判断的话，每次下的代码是该学生最近提交该题的ac代码，如果将这个if语句去掉，那么下的代码就是该学生第一次提交该题的ac代码
                            continue
                        soup = BeautifulSoup(txt, "html.parser")
                        with open(loc2, 'w', encoding='utf-8') as f: # 写入代码
                            f.write(soup.pre.text)
                except Exception:
                    print("出错了，在第" + str(page)+"页的第"+i + "行")
                    # break

acm = ojpc('root', '123456789')
contestId = input("请输入比赛id号:")
totalSubmit = input("请输入整场比赛总的提交数目:")
totalSubmit = int(totalSubmit)
pagenum = acm.getPages(totalSubmit)
print(pagenum)
contestIdPos = contestUrl.find("&userName")
n_contestUrl = contestUrl[0:contestIdPos] + contestId + contestUrl[contestIdPos:len(contestUrl)]
acm.run(pagenum, n_contestUrl)
print("done....")
