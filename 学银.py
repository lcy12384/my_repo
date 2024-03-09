import requests
from lxml import etree
import re
import json
from ip代理池 import cre_headers,cre_proxies
from concurrent.futures import ThreadPoolExecutor

def get_course_url(url):
    domain = 'https://xueyinonline.com'
    resp = requests.get(url, headers=cre_headers(), proxies=cre_proxies())
    et = etree.HTML(resp.text)
    result = et.xpath('//div[@class = "qExpress_pic"]/a/@href')
    url_result = []
    for item in result:
        url_result.append(domain + item)
    return url_result

def get_course_inf(url, f):
    resp = requests.get(url, headers=cre_headers(), proxies=cre_proxies())
    obj = re.compile(r'<div class="mainCourse">.*?value="(?P<id>.*?)"/>.*?<div class="mgCard_con fr">.*?title=".*?">(?P<name>.*?)<.*?'
                     r'主讲教师：(?P<teacherwithschool>.*?)</dd>', re.S)
    result = obj.search(resp.text)
    dic = result.groupdict()
    if not dic['teacherwithschool'].isspace():
        dic['teacher'] = dic['teacherwithschool'].split(" /",2)[0]
        dic['school'] = dic['teacherwithschool'].split(" /", 2)[1]
        dic['teacher'] = dic['teacher'].strip()
        dic['school'] = dic['school'].strip()
    else:
        dic['teacher'] = ''
        dic['school'] = ''
    del dic['teacherwithschool']
    #课程名称、课程id、主讲教师、学校
    obj = re.compile(r'function getEvaluate.*?enc: "(?P<enc>.*?)",.*?starttime: "(?P<starttime>.*?) 00.*?endtime: "(?P<endtime>.*?) 23', re.S)
    result = obj.search(resp.text)
    dic_tem = result.groupdict()
    domain = 'https://xueyinonline.com/course/getevaluate?courseid='+dic['id']+'&enc='+dic_tem['enc']+'&starttime='+dic_tem['starttime']+'+00%3A00%3A00&endtime='+dic_tem['endtime']+'+23%3A59%3A59&size=50'
    resp_tem = requests.get(domain, headers=cre_headers(),proxies=cre_proxies())
    obj = re.compile(r'课程评分：</span><span class="big_num"> (?P<scores>.*?)</span>.*?共(?P<commentsCount>.*?)人评价', re.S)
    result = obj.search(resp_tem.text)
    dic_tem = result.groupdict()
    dic.update(dic_tem)
    #课程评分、评论数
    domain = "https://xueyinonline.com/statistics/api/stattistics-data?courseId="
    resp = requests.get(domain + dic['id'], headers=cre_headers(),proxies=cre_proxies())
    dic.update(json.loads(resp.text))
    dic['url'] = url
    #累计页面浏览量、累计选课人数、累计互动次数
    resp = requests.get(url, headers=cre_headers(), proxies=cre_proxies())
    et = etree.HTML(resp.text)
    course_ex_inf = et.xpath("//dl[@class = 'mgCard_deta']/dt/span/@class")
    if course_ex_inf == []:
        dic['courseLevel'] = "普通课程"
    else:
        if course_ex_inf[0] == 'qTips_one':
            dic['courseLevel'] = '国家一流课程'
        else:
            dic['courseLevel'] = '省精品课程'
    # 课程等级
    course_ex_inf = et.xpath("//span[@class = 'mgCard_dijiqi_con']/a/text()")
    course_ex_inf_cur = et.xpath("//span[@class = 'mgCard_dijiqi_con']/a/@href")
    course_ex_inf_cur = ["https://www.xueyinonline.com/" + i for i in course_ex_inf_cur]
    course_ex_inf = [list(i) for i in zip(course_ex_inf, course_ex_inf_cur)]
    dic['qici'] = course_ex_inf
    # 期次
    course_ex_inf = et.xpath("//dl[@class ='mgCard_deta']/dd[3]/text()")
    dic['endtime'] = course_ex_inf
    # 起止日期
    course_ex_inf = et.xpath("//dl[@class ='mgCard_deta']/dd[4]/span/a[@class = 'current']/text()")
    dic['status'] = course_ex_inf
    # 教学进度
    domain = 'https://www.xueyinonline.com/detail/introduce?courseId=' + dic['id'] + '&orgCourseId=' + dic['id']
    resp_tem = requests.get(domain, headers=cre_headers(), proxies=cre_proxies())
    et = etree.HTML(resp_tem.text)
    course_ex_inf = et.xpath("//div[@class = 'kc_intro_text  clearAfter']/p[@style = 'white-space: normal;']/text()")
    dic['introduce'] = course_ex_inf
    # 说明、适用人群
    json_inf = json.dumps(dic, ensure_ascii=False)
    f.write(json_inf + '\n')
    return dic

def get_course_dir(url, f):
    #{'id':'***', 'dir':'1.1 ***'}
    resp = requests.get(url, headers=cre_headers(),proxies=cre_proxies())
    obj = re.compile(r'<div class="mainCourse">.*?value="(?P<id>.*?)"/>', re.S)
    result = obj.search(resp.text)
    dic = result.groupdict()
    resp = requests.get('https://xueyinonline.com/detail/knowledge-catalog?courseId='+dic['id']+'&orgCourseId='+dic['id'], headers=cre_headers(), proxies=cre_proxies())
    et = etree.HTML(resp.text)
    course_dir = et.xpath('//a/text()')
    course_dir_unreadable = et.xpath('//span[@class = "unreadable"]/text()')
    li = []
    for item in course_dir:
        item = item.strip()
        item = ''.join(item.split())
        li.append(item)
    if course_dir_unreadable != None:
        for item in course_dir_unreadable:
            item = item.strip()
            item = ''.join(item.split())
            li.append(item)
    dic['dir'] = li
    json_dir = json.dumps(dic, ensure_ascii=False)
    f.write(json_dir + '\n')

def main():
    with ThreadPoolExecutor(10) as task:
        for i in range(678, 1226):
            url = "https://xueyinonline.com/mooc/categorycourselist?categoryid=0&coursetype=0&page="
            url = url + f"{i}"
            url_result = get_course_url(url)
            # 课程名称、课程id、主讲教师、学校、累计页面浏览量、累计选课人数、累计互动次数、课程评分、评论数
            f_inf = open(f'D:/WorkSpace/毕业设计/xueyin_course_inf-2024.3.7/page{i}.txt', 'w', encoding='utf-8')
            f_dir = open(f'D:/WorkSpace//毕业设计/xueyin_course_dir-2024.3.7/page{i}.txt', 'w', encoding='utf-8')
            for course_url in url_result:
                task.submit(lambda cxp:get_course_inf(*cxp), (course_url, f_inf))
                task.submit(lambda cxp:get_course_dir(*cxp), (course_url, f_dir))
    print('all finish!!')
if __name__ == '__main__':
    main()