import requests
import json
import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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
    # print(driver.page_source)
    # print(course_url)
    while(True):
        et = etree.HTML(driver.page_source)
        course_name = et.xpath('//span[@class="f-thide u-courseCardWithTime-teacher_span162"]/text()')
        course_url = et.xpath('//a[@class="u-courseCardWithTime-container_a160"]/@href')
        for item in list(zip(course_name, course_url)):
            course["name"] = item[0]
            course["url"] = item[1]
            course["school"] = school_with_url[0]
            get_course_inf(course)
        driver.find_element(by=By.XPATH, value='//div[@id="j-courses"]/div[@class="u-ctlist"]/div[2]/div/a[11]').click()
        time.sleep(3)
        if(et.xpath('//div[@id="j-courses"]/div[@class="u-ctlist"]/div[2]/div/a[11]/@class')) == ["zbtn znxt js-disabled"]:
            break

def get_course_inf(course):
    print(course)

def main():
    # school_with_url = get_school_url()
    a = [('北京大学', 'https://www.icourse163.org/university/PKU'),('error!!', 'error!!')]
    get_course_url(a[0])
if __name__ =='__main__':
    main()