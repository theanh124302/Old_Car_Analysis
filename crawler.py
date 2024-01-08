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


def reformat(values):
    try:
        values = values.strip()
        values = values.replace("\n", "")
        values = values.replace("\t", "")
    except:
        pass

    return values

def preprocess(data):
    data['year'] = int(data['year']) if data['year'] != '-' else None
    data['driven kms'] = int(data['driven kms'].split(" ")[0].replace(',','')) if data['driven kms'] != '-' else None
    data['num_of_door'] = int(data['num_of_door'].split(' ')[0]) if data['num_of_door'] != '-' else None
    data['num_of_seat'] = int(data['num_of_seat'].split(' ')[0]) if data['num_of_seat'] != '-' else None
    data['engine_type'] = data['engine_type'].split(' ')[0] if data['engine_type'] != '-' else None
    
    # price = data['price'].strip().split(' ')
    # bid = price.index('Tỷ') if 'Tỷ' in price else -1
    # mid = price.index('Triệu') if 'Triệu' in price else -1  
    # b_value = float(price[bid-1]) if bid > 0 else 0
    # m_value = float(price[mid-1]) if mid > 0 else 0
    # data['price' ] = b_value + m_value/1000       
    data['transmission'] = data['transmission'] if data['transmission'] != '-' else None
    return data
def extract_information(url):
    try:    
        url = url.replace('\n','')
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
    
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        infors = soup.find_all('span', attrs = {'class': 'inp'})
        inf_title = soup.find('div', attrs = {'class': 'title'})
        title = inf_title.find('h1').text.split('-')
        name = title[0]
        price = title[1]

        infor_car = [infor.text.strip() for infor in infors]
        print(infor_car)        
        data = {
            'car_name': reformat(name),
            'year': reformat(infor_car[0]),
            'price': reformat(price),
            'assemble_place': infor_car[3],
            'series': reformat(infor_car[4]),
            'driven kms': reformat(infor_car[2]),
            'num_of_door': reformat(infor_car[10]),
            'num_of_seat': reformat(infor_car[9]),
            'engine_type': reformat(infor_car[6]),
            'transmission': reformat(infor_car[5]),
            'url': url.replace('\n','')
        }
        # field = ['car_name','year','price','assemble_place','series','driven kms','num_of_door','num_of_seat','engine_type','transmission','url']
        data = preprocess(data)
        return data
        # print(box)
        # with open("Data/data.json", 'a', encoding= 'utf-8') as file:
        #     json.dump(data,file,indent= 4 , ensure_ascii= False)
        #     file.write(',')
    #     with open("Data/data.csv", 'a', encoding= 'utf-8') as csvfile:
    #         writer = csv.DictWriter(csvfile, fieldnames= field)
            
            # writer.writerow(data)
    except Exception as e:
        print(e)




if __name__ == '__main__':
    #  threads = []
    #  for i in range(1,3):
    #       t = multiprocessing.Process(target= extract_information, args = (i,))
    #       threads.append(t)
    #  for t in threads:
    #       t.start()
    #  for t in threads:
    #       t.join()
    car_data = []
    field = ['car_name','year','price','assemble_place','series','driven kms','num_of_door','num_of_seat','engine_type','transmission','url']
    
        
    with open('Data/link_old_car.txt', 'r') as file:
        links = file.readlines()
        file.close()
    cnt = 0
    for link in links:
        cnt += 1
        if cnt > 10: 
            break
        data = extract_information(link)
        car_data.append(data)
        
    with open("Data/data1.csv", 'a', encoding= 'utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames= field)
        writer.writeheader()
        writer.writerows(car_data)
    
        
            
     
            
        
    
    

    