
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import csv

import os



def get_coords(location: str) -> tuple:
    """Return coordinates for a given location"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    browser = webdriver.Chrome('C:/Program Files/Chromedriver/chromedriver.exe', options=chrome_options)
    browser.get(f'https://plus.codes/map/{str(location)}')

    time.sleep(5)

    html = BeautifulSoup(
        browser.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        ),
        features='lxml'
    )

    browser.quit()

    coords = html.find('div', class_= 'detail latlng clipboard vertical-center')

    if coords == None:
        raise Exception('No internet connection')
    else:
        return tuple(coords.string.split(','))



def get_grid_index(coords: tuple) -> str:
    """returns the index of the grid field in which the coords lie"""
    pass


def get_precipitation_heights(grid_index: str, return_period=None) -> list:
    """scans all csv-sheets to return a list of precipitation heights for a given grid_index and return period.
    If return period is None values for all periods will be listed"""
    os.chdir(r'./DWD_Regenspenden')     #change to directory with the files containing precipitation heights

    period_to_col = {1: 1, 2: 2, 3: 3, 5: 4, 10: 5, 20: 6, 30: 7, 50: 8, 100: 9}
    heights = []
    
    for f in sorted(os.listdir()):
        with open(f) as cf:
            reader = csv.reader(cf, delimiter=';')
            
            for row in reader:
                if grid_index == row[0]:
                    if return_period == None:
                        heights.append(row[1:])
                    else:
                        heights.append([row[period_to_col[return_period]]])

                    break
    
    os.chdir('..')  #change to start-location, in case of repeated calls

    return heights
        


def save_precipitation_heights(prec_heigths: list):
    """saves the list from *get_precipitation_heights* to a csv-file"""
    with open("test.csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        for heigth in prec_heigths:
            writer.writerow(heigth)

    #TODO include address, coordinates, grid index
        




#print(get_coords("Wirtshalde 5 Dietmannsried"))

liste = get_precipitation_heights("92036")

save_precipitation_heights(liste)
