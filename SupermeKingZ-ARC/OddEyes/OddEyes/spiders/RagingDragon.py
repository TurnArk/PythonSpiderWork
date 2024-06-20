# -*- coding: GBK -*-
import csv
import time
import scrapy
import chardet
from selenium import webdriver
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .picturer import ZARC
class Message(scrapy.Item):
    name = scrapy.Field()
    type = scrapy.Field()
    year = scrapy.Field()
    number = scrapy.Field()


class RagingdragonSpider(scrapy.Spider):
    name = "RagingDragon" #
    allowed_domains = ["www.bilibili.com"] #
    start_urls = ["https://www.bilibili.com/anime/index/"] #
    custom_settings = {
        'ROBOTSTXT_OBEY':False,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 543,
        },
    }

    def start_requests(self): #
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
                }
            )

    def emptyDelete(self,text,xpath_str):
        data=text.xpath(xpath_str).get()
        if data:
            return data.strip()
        return None

    def writeData(self,page_source,now_year,i):
        t_list = scrapy.Selector(text=page_source).xpath(
            ".//div[@class='filter-body']//ul[@class='bangumi-list clearfix']//li[contains(@class,'bangumi-item')]")
        url_data = '../Data/data.csv'
        with open(url_data, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
        file = open(url_data, 'a+', encoding=encoding)
        for text in t_list:
            item = Message()
            item['year'] = self.emptyDelete(text,f'../../../..//ul[@class="filter-item-wrapper free"]//li[@title="{now_year}"]/text()')
            item['type'] = self.emptyDelete(text,f'../../../..//div[contains(text(),"风格")]/following-sibling::ul[1]//li[contains(@class,"filter-item")][{i}]/text()')
            item['number'] = self.emptyDelete(text, './/div[@class="shadow"]/text()')
            item['name'] = self.emptyDelete(text, './/a[@class="bangumi-title"]/text()')
            print(f"\nItem details - Name: {item['name']}, Type: {item['type']}, Year: {item['year']}, Number: {item['number']}\n")
            #print(f"\nItem details - Name: {item['name']},  Number: {item['number']}\n")
            print(item)
            data = f"{item['year']},{item['type']},{item['name'].replace(',','，')},{item['number']}\n"
            #data = f"{item['name']},{item['number']}\n"
            file.write(data)
        file.close()

    def clickOnLast(self,driver,page_source,year,i):
        while True:
            try:
                WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//ul[@class='bangumi-list clearfix']//li[contains(@class,'bangumi-item')]")))
                time.sleep(3)
                self.writeData(page_source,year,i)
                button = WebDriverWait(driver,20).until(
                    EC.element_to_be_clickable((By.XPATH,"//div[@class='pagelistbox clearfix']//a[contains(@class,'p next-page')]")))
                # scroll_by = button.location['y']  # 获取按钮位置
                # driver.execute_script("window.scrollTo(0,arguments[0])", scroll_by+200)  # 滚动到按钮位置
                time.sleep(1)
                button.click()
            except:
                print("最后一页了\n")
                break

    def numberHandle(self,num):
        if num[-3] == '万':
            return int(float(num[0:-3])*10000)
        elif num[-3] == '亿':
            return int(float(num[0:-3])*100000000)
        else:
            return int(num[0:-2])

    def dataHandle(self):
        print("少女折寿中...")
        dict = {2018: {}, 2019: {}, 2020: {}, 2021: {}, 2022: {}, 2023: {}}
        url_path = '../Data/data.csv'
        url_path_handle = '../Data/dataHandle.csv'
        with open(url_path, 'r') as f:
            lists = csv.reader(f)
            for item in lists:
                year=int(item[0])
                if item[1] not in dict[year]:
                    dict[year][item[1]]=0
                dict[year][item[1]]+=self.numberHandle(item[3])
        keys = list(dict.keys())
        with open(url_path_handle, 'a+') as file:
            file.write(f"year,classes,number\n")
            for year in keys:
                key = list(dict[year].keys())
                for ty in key:
                    print(f"{year},{ty},{dict[year][ty]}")
                    file.write(f"{year},{ty},{dict[year][ty]}\n")


    def parse(self, response):
        driver =webdriver.Edge()
        driver.get(self.start_urls[0])
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@class,'filter-item')]")))#等筛选列表加载好
            driver.execute_script("window.scrollTo(0,arguments[0])",150)#把悬浮窗骗出来
            time.sleep(2)
            CRNMSL=WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[(@data-v-7b35db32 or @data-v-451e8e8e) and @class='lt-row']")))#等悬浮窗加载
            driver.execute_script("""
                var div=arguments[0];
                div.parentNode.removeChild(div);
                """, CRNMSL) #关掉那个弹出来挡住按钮的大会员悬浮弹窗
            time.sleep(3)
            for year in range(2018,2024):
                year_path=f"//ul[@class='filter-item-wrapper free']//li[contains(@class,'filter-item') and @title='{year}']"
                button_year = driver.find_element(By.XPATH, year_path)#找到对应年份的元素
                # scroll_yy=button_year.location['y']#获取按钮位置
                # driver.execute_script("window.scrollTo(0,arguments[0])",scroll_yy-300)#滚动到按钮位置
                button_year.click()
                time.sleep(3)
                for i in range(2,11):
                    type_path=f"//div[contains(text(),'风格')]/following-sibling::ul[1]//li[contains(@class,'filter-item')][{i}]"
                    button_type= driver.find_element(By.XPATH, type_path) #找到对应风格的元素
                    # scroll_ty = button_type.location['y']  # 获取按钮位置
                    # driver.execute_script("window.scrollTo(0,arguments[0])", scroll_ty-300)  # 滚动到按钮位置
                    button_type.click()
                    time.sleep(3)
                    self.clickOnLast(driver,driver.page_source,year,i)
        finally:
            driver.close()
            self.dataHandle()
            ZARC().draw('../Data/dataHandle.csv','../Font/simsunb.ttf')

