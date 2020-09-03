
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import pandas as pd
import itertools

import csv

import os


period_to_col = {1: 1, 2: 2, 3: 3, 5: 4, 10: 5, 20: 6, 30: 7, 50: 8, 100: 9}

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
        coords = [float(coord) for coord in coords.string.split(',')]
        return tuple(coords)



def get_grid_index(coords: tuple) -> str:
    """returns the index of the grid field in which the coords are located"""
    as_lat = round(530/41*(55.2-coords[0]))     #first assumption for grid location
    as_lng = round(7.5*(coords[1]-5.3))
    print(as_lat, as_lng)

    test_row = list(range(as_lat-2, as_lat+3))
    test_col = list(range(as_lng-2, as_lng+3))
    pd_indices = (79*row + col for row, col in itertools.product(test_row, test_col))
    
    print(pd_indices)
    df = pd.read_excel('KOSTRA-DWD-2010R_geog_Bezug.xlsx', sheet_name='Raster_geog_Bezug')
    for i in pd_indices:
        print(df.iloc[i][0])




def get_precipitation_heights(grid_index: str, return_period=None) -> list:
    """scans all csv-sheets to return a list of precipitation heights for a given grid_index and return period.
    If return period is None values for all periods will be listed"""
    os.chdir(r'./DWD_heights')     #change to directory with the files containing precipitation heights

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
        


def save_precipitation_heights(prec_heigths: list, metadata: tuple):
    """saves the list from *get_precipitation_heights* to a csv-file"""
    duration = [5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 540, 720, 1080, 1440, 2880, 4320]

    with open("test.csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows([["location", "latitude", "longitude", "grid_index"], metadata])
        
        writer.writerows([[], ["[min]\\[a]"] + list(period_to_col.keys())])

        for i, heigth in enumerate(prec_heigths):
            writer.writerow([duration[i]] + heigth)

    #TODO include address, coordinates, grid index
        




#print(get_coords("Oberbalzheim"))

get_grid_index((48.162, 10.082))

#liste = get_precipitation_heights("92036")

#save_precipitation_heights(liste, ("test", "10.1", "43.2", "92036"))
