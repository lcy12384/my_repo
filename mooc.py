import requests
import json
import re
import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from ip代理池 import cre_headers,cre_proxies
from concurrent.futures import ThreadPoolExecutor
import os

def get_school_url():
    driver = webdriver.Edge()
    driver.get('https://www.icourse163.org/university/view/all.htm#/')
    et = etree.HTML(driver.page_source)
    channel_name = et.xpath('//img/@alt')
    channel_url = et.xpath('//a[@class="u-usity f-fl"]/@href')
    channel_url = map(lambda x: 'https://www.icourse163.org' + x, channel_url)
    return list(zip(channel_name, channel_url))

def get_course_url(school_with_url):
    course = {}
    driver = webdriver.Edge()
    driver.get(school_with_url[1])
    while(True):
        et = etree.HTML(driver.page_source)
        course_name = et.xpath('//span[@class="f-thide u-courseCardWithTime-teacher_span162"]/text()')
        course_url = et.xpath('//a[@class="u-courseCardWithTime-container_a160"]/@href')
        for item in list(zip(course_name, course_url)):
            course["name"] = item[0]
            course["url"] = "https:" + item[1]
            course["school"] = school_with_url[0]
            get_course_inf(course)
        driver.find_element(by=By.XPATH, value='//div[@id="j-courses"]/div[@class="u-ctlist"]/div[2]/div/a[11]').click()
        time.sleep(3)
        if(et.xpath('//div[@id="j-courses"]/div[@class="u-ctlist"]/div[2]/div/a[11]/@class')) == ["zbtn znxt js-disabled"]:
            break

def get_course_inf(course):
    url = course["url"]
    # name,url,school,teacher,id,chooseCount,commentsCount,scores
    res = requests.get(url,headers=cre_headers())
    obj_inf = re.compile('enrollCount : "(?P<chooseCount>.*?)",.*?id : "(?P<id>.*?)"',re.S)
    obj_dir = re.compile('name: "(?P<dir_name>.*?)".*?goals: "(?P<dir_goals>.*?)".*?plan: "(?P<dir_plan>.*?)"',re.S)
    obj_teacher = re.compile('lectorName : "(?P<teacher_name>.*?)".*?lectorTitle : "(?P<teacher_title>.*?)"',re.S)
    obj_dir_null = re.compile('overflow-wrap: break-word; font-size: 13px;\\\\">(?P<dir>.*?)<')
    result_inf = obj_inf.search(res.text)
    course.update(result_inf.groupdict())
    course['dir'] = obj_dir.findall(res.text)
    if course['dir'] == []:
        course['dir'] = obj_dir_null.findall(res.text)
    course['teacher'] = obj_teacher.findall(res.text)
    #名字、id、教师、目录、选课人数
    driver = webdriver.Edge()
    driver.get(url)
    driver.find_element(by=By.XPATH, value='//div[@id="review-tag-button"]').click()
    time.sleep(2)
    et = etree.HTML(driver.page_source)
    result_scores = et.xpath('//div[@class="ux-mooc-comment-course-comment_head_rating-scores"]/span/text()')
    result_commentsCount = et.xpath('//div[@class="ux-mooc-comment-course-comment_head_rating-action_tips"]/span/text()')
    if not result_scores == []:
        course['scores'] = result_scores[0]
    else:
        course['scores'] = '0'
    if not result_commentsCount == []:
        course['commentsCount'] = re.search('共 (?P<commentsCount>.*?) 条评价',result_commentsCount[0]).groupdict()['commentsCount']
    else:
        course['commentsCount'] = '0'
        #分数、评论数
    f_school = course['school']
    f_name = course['name']
    if not os.path.exists(f'F:/WorkSpace/mooc/{f_school}'):
        os.mkdir(f'F:/WorkSpace/mooc/{f_school}')
    f = open(f'F:/WorkSpace/mooc/{f_school}/{f_name}.txt', 'w', encoding='utf-8')
    json_course = json.dumps(course, ensure_ascii=False)
    f.write(json_course)
    f.close()

def main():
    school_with_url = get_school_url()
    with ThreadPoolExecutor(10) as task:
        for item in school_with_url:
            task.submit(get_course_url, item)

if __name__ =='__main__':
    main()