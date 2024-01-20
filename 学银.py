import requests
from lxml import etree
import re
import json
from fake_useragent import UserAgent

def cre_headers():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    return headers

def get_course_url(url):
    domain = 'https://xueyinonline.com'
    resp = requests.get(url, headers=cre_headers())
    et = etree.HTML(resp.text)
    result = et.xpath('//div[@class = "qExpress_pic"]/a/@href')
    url_result = []
    for item in result:
        url_result.append(domain + item)
    return url_result

def get_course_inf(url):
    resp = requests.get(url, headers=cre_headers())
    obj = re.compile(r'<div class="mainCourse">.*?value="(?P<id>.*?)"/>.*?<div class="mgCard_con fr">.*?title=".*?">(?P<name>.*?)<.*?'
                     r'主讲教师：(?P<teacher>.*?) /(?P<school>.*?)</dd>', re.S)
    result = obj.search(resp.text)
    dic = result.groupdict()
    dic['teacher'] = dic['teacher'].strip()
    dic['school'] = dic['school'].strip()
    #课程名称、课程id、主讲教师、学校
    obj = re.compile(r'function getEvaluate.*?enc: "(?P<enc>.*?)",.*?starttime: "(?P<starttime>.*?) 00.*?endtime: "(?P<endtime>.*?) 23', re.S)
    result = obj.search(resp.text)
    dic_tem = result.groupdict()
    domain = 'https://xueyinonline.com/course/getevaluate?courseid='+dic['id']+'&enc='+dic_tem['enc']+'&starttime='+dic_tem['starttime']+'+00%3A00%3A00&endtime='+dic_tem['endtime']+'+23%3A59%3A59&size=50'
    resp_tem = requests.get(domain, headers=cre_headers())
    obj = re.compile(r'课程评分：</span><span class="big_num"> (?P<scores>.*?)</span>.*?共(?P<commentsCount>.*?)人评价', re.S)
    result = obj.search(resp_tem.text)
    dic_tem = result.groupdict()
    dic.update(dic_tem)
    #课程评分、评论数
    domain = "https://xueyinonline.com/statistics/api/stattistics-data?courseId="
    resp = requests.get(domain + dic['id'], headers=cre_headers())
    dic.update(json.loads(resp.text))
    dic['url'] = url
    #累计页面浏览量、累计选课人数、累计互动次数
    return dic

def get_course_dir(course):
    #{'id':'***', 'dir':'1.1 ***'}
    dic = {'id': course['id']}
    resp = requests.get('https://xueyinonline.com/detail/knowledge-catalog?courseId='+dic['id']+'&orgCourseId='+dic['id'], headers=cre_headers())
    et = etree.HTML(resp.text)
    course_dir = et.xpath('//a/text()')
    li = []
    for item in course_dir:
        item = item.strip()
        item = ''.join(item.split())
        li.append(item)
    dic['dir'] = li
    return dic

def main():
    for i in range(1,51):
        url = "https://xueyinonline.com/mooc/categorycourselist?categoryid=0&coursetype=0&page="
        url = url + f"{i}"
        url_result = get_course_url(url)
        # 课程名称、课程id、主讲教师、学校、累计页面浏览量、累计选课人数、累计互动次数、课程评分、评论数
        f_inf = open(f'F:/WorkSpace/xueyin_course_inf/page{i}.txt', 'w', encoding='utf-8')
        f_dir = open(f'F:/WorkSpace/xueyin_course_dir/page{i}.txt', 'w', encoding='utf-8')
        for course_url in url_result:
            course = get_course_inf(course_url)
            json_inf = json.dumps(course, ensure_ascii=False)
            f_inf.write(json_inf + '\n')
            course_dir = get_course_dir(course)
            json_dir = json.dumps(course_dir, ensure_ascii=False)
            f_dir.write(json_dir + '\n')
        print(f"第{i}页完成.")
    print('all finish!!')

if __name__ == '__main__':
    main()