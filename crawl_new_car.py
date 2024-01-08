from selenium import webdriver
from bs4 import BeautifulSoup
from time import time 
import multiprocessing
import threading
import json


def process_descriptions(description):
    descript = description.split(',')
    assemble_place = descript[0].strip().replace('*', '')
    # transmission = descript[-1].replace('...','').strip()
    # return assemble_place, transmission
    return assemble_place
    
# car = []

def get_car(i,share_list):
    try:
        url = f"https://bonbanh.com/oto-xe-moi/page,{i}"
        driver = webdriver.Chrome()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cars = soup.find_all("li", "car-item")
        # data_cars = []
        for _car in cars:
            type = _car.find('div', 'cb1').text
            name = _car.find('div','cb2_02').text
            price = _car.find('div','cb3').text
            description = _car.find('div','cb6_02').text
            assemble_place = process_descriptions(description)
            data = {
                'name':name,
                'price':price,
                'type':type,
                'assemble_place': assemble_place,
                # 'transmission': transmission
            }
            # global car
            share_list.put(data)
    except Exception as e:
        print(e)
    # with open("Data/page_2.json", 'w', encoding='utf-8') as json_file:
    #     json.dump(data_cars, json_file,ensure_ascii=False , indent = 4)

# if __name__ == '__main__':
    #  threads = []
    #  car = []
    #  for i in range(1,10):
    #       t = multiprocessing.Process(target= get_car, args = (i,))
    #       threads.append(t)
    #  for t in threads:
    #       t.start()
    #  for t in threads:
    #       t.join()
if __name__ == '__main__':
   
    manage = multiprocessing.Manager()
    car = manage.Queue()
    result_list = []
   
    for i in range(1,72):
        threads = []
        for j in range(5*i,5*(i+1)):
            t = multiprocessing.Process(target= get_car, args = (j,car))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        while not car.empty():
            result_list.append(car.get())
    # print(car)
    # car.extend(data_car)
    with open("Data/new_car_data.json", 'w', encoding='utf-8') as json_file:
        json.dump(result_list, json_file,ensure_ascii=False ,    indent = 4)