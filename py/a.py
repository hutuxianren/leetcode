
#coding:utf-8
from urllib.request import urlopen
from urllib2 import urlopen
import  cookielib, re
import ssl 
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" ) #编码方式
ssl._create_default_https_context = ssl._create_unverified_context
NAME = 'tuyixin1993@163.com'
PWD = 'tuyixin20112902' #用户名和密码
BASE_URL = 'https://leetcode.com/'  #域名

def login(user, password): #登陆
	login_page = BASE_URL + 'accounts/login/'
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [
		('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko')
	]
	ptn = re.compile(".*name='csrfmiddlewaretoken' value='(.*)'.*")
	login_page_data = opener.open(login_page).read()
	csrfmiddlewaretoken = ptn.search(login_page_data).group(1)
	data = urllib.urlencode({"csrfmiddlewaretoken":csrfmiddlewaretoken, "login":user, "password":password})
	opener.addheaders.append(('Referer', 'https://leetcode.com/accounts/login/'))
	opener.open(login_page, data)
	if opener == None:
		print ("Failed to login.")
		exit(-1)
	return opener
	
def get_links(opener):
	links = {}
	page_num = 60
	while True:
		print ("Getting submissions...page %d"%page_num)
		submissions_url = BASE_URL + 'submissions/%d/' % page_num
		pattern = 'href="/problems/(.*)/".*\s*</td>\s*<td>\s*.*href="/(submissions/detail/[0-9]*/).*Accepted.*\s*</td>\s*<td>\s*(.*) ms' #获取ac链接，正则表达式
		submissions = re.findall(pattern, opener.open(submissions_url).read())
		if page_num == 82: #提交代码的总页数
			break
		for submission in submissions: 
			key = submission[0]
			if not links.has_key(key) or int(links[key][1]) > int(submission[2]):
				links[key] = submission[1:3]
		page_num += 1
	return links
	
def save_accepted_code(opener, problem_name, url):
	print ("Querying %s...") % url
	pattern = "vm.code.*'([\s\S]*)';" #获取Ac代码的位置
	code = re.findall(pattern, opener.open(url).read())[0].decode("utf-8")
	toCpp = {'\u000D':'\n','\u000A':'','\u003B':';','\u003C':'<','\u003E':'>','\u003D':'=','\u0026':'&','\u002D':'-','\u0022':'"','\u0009':'/t','\u0027':"'"}
	#改编码
	for key in toCpp:
		code = code.replace(key,toCpp[key])
	#code = json.loads(code)
	f = file('%s.cpp' % problem_name, 'wb')
	f.write(code)
	f.close() #写文件
	print ("Saved %s.") % problem_name
	
if __name__ == '__main__':
	print ("Login...")
	opener = login(NAME, PWD)
	links = get_links(opener)
		
	for key in links.keys():
		save_accepted_code(opener, key, BASE_URL + links[key][0])
