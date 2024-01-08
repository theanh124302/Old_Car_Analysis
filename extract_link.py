from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import threading
import time  
import multiprocessing
from html import unescape
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_links_car(index):
    pages = [f"https://bonbanh.com/oto-xe-cu/page,{i}" for i in range(index*5,(index+1)*5)]
    # print(pages)
    for page in pages:
        driver = webdriver.Chrome()
        driver.get(page) 
        page_source = driver.page_source
        if "Vui Lòng Tick vào ô" in driver.page_source:
                    while "Vui Lòng Tick vào ô" in page_source:
                        page_source = driver.page_source
                        time.sleep(1)
        else:
            soup = BeautifulSoup(driver.page_source,'html.parser')
            
            cars = soup.find_all("li", "car-item")
            links = [car.find('a', attrs = {'itemprop': 'url'}) for car in cars]
            urls = []
            for link in links:
                url = link.get('href')
                url = "https://bonbanh.com/" + url
                urls.append(url)
                
            with open("Data/link_old_car.txt", 'a') as file:
                file.writelines('\n'.join(urls))
                file.write('\n')
            driver.close()

if __name__ == '__main__':
     threads = []
     for i in range(1,2):
          t = multiprocessing.Process(target= get_links_car, args = (i,))
          threads.append(t)
     for t in threads:
          t.start()
     for t in threads:
          t.join()
     