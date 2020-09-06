import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd

import csv

import os


period_to_col = {1: 1, 2: 2, 3: 3, 5: 4, 10: 5, 20: 6, 30: 7, 50: 8, 100: 9}    #column in csv that corresponds to return-period

def get_coords(location: str) -> tuple:
    """Return coordinates for a given location"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    browser.get(f'https://plus.codes/map/{str(location)}')      #open website to retrieve coordinates

    time.sleep(3)                                               #wait for website to load

    html = BeautifulSoup(                                       #extract html-structure
        browser.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        ),
        features='lxml'
    )

    browser.quit()                                              #close browser

    coords = html.find('div', class_= 'detail latlng clipboard vertical-center')    #extract coordinates

    if coords == None:
        raise Exception('No internet connection')
    else:
        coords = [float(coord) for coord in coords.string.split(',')]               #split text into y and x value
        return tuple(coords)



def get_grid_index(coords: tuple) -> str:
    """returns the index of the grid field in which the coords are located"""
    est_lat = round(530/41*(55.2-coords[0]))    #first estimation for grid location
    est_lng = round(7.5*(coords[1]-5.3))
    
    as_lat = est_lat                            #save to other variable to have original value
    as_lng = est_lng

    def check_borders(data, tup: tuple, lng: float) -> bool:
        """interpolates a point on a border according to a given longitude"""
        return (data[tup[3]] - data[tup[1]])/(data[tup[2]] - data[tup[0]])*(lng - data[tup[0]]) + data[tup[1]]
    
    df = pd.read_excel('KOSTRA-DWD-2010R_geog_Bezug.xlsx', sheet_name='Raster_geog_Bezug')  #load excel-file
    
    #algorithm is based on the cognition, that the grid fields are tilted to the right
    while True:
        pd_index = 79*as_lat + as_lng                                   #get index corresponding to assumed grid field
        row = df.iloc[pd_index]                                         #save row to minimize pandas calls 

        if check_borders(row, (8, 9, 10, 11), coords[1]) > coords[0]:   #bottom border: if border latitude bigger real
            as_lat += 1                                                     #latitude go one grid field down
            continue
        if check_borders(row, (6, 7, 12, 13), coords[1]) < coords[0]:   #top border: if border latitude smaller real
            as_lat -= 1                                                     #latitude go one grid field up
            continue
                                                                        
        if check_borders(row, (10, 11, 12, 13), coords[1]) > coords[0]: #right border: if border latitude bigger real
            as_lng += 1                                                     #latitude go one field to the right 
            continue
        if check_borders(row, (8, 9, 6, 7), coords[1]) < coords[0]:     #left border: if border latitude smaller real
            as_lng -= 1                                                     #latitude gon one field to the left
            if as_lng < est_lng - 5:                #security feature: if estimated grid is more than two columns
                as_lng = est_lng + 5                    #to the left, algorithm would count down to negative values
            continue
        
        break 

    return str(1000*as_lat + as_lng)                #convert grid indizes to one identifier



def get_precipitation_heights(grid_index: str, return_period=None) -> list:
    """scans all csv-sheets to return a list of precipitation heights for a given grid_index and return period.
    If return period is None values for all periods will be listed"""
    os.chdir(r'./DWD_heights')     #change to directory with the files containing precipitation heights

    if return_period == None:                                       #initialize list with header
        heights = [["[min]\\[a]"] + list(period_to_col.keys())]         #depending whether a return period is given
    else:
        heights = [["[min]\\[a]", return_period]]
    
    for f in sorted(os.listdir()):                      #iterate over sorted files, to prevent a mess
        with open(f) as cf:
            reader = csv.reader(cf, delimiter=';')      #create iterator over csv-file
            
            for row in reader:
                if grid_index == row[0]:                #search until row containing grid index
                    if return_period == None:
                        heights.append(row[1:])         #no return period specified: save all
                    else:
                        heights.append([row[period_to_col[return_period]]])     #save only requested return period

                    break
    
    os.chdir('..')              #change to start-location, in case of repeated calls

    return heights
        


def save_precipitation_heights(filename: str, prec_heigths: list, metadata: dict):
    """saves the list from *get_precipitation_heights* to a csv-file"""
    duration = [5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 540, 720, 1080, 1440, 2880, 4320]

    with open(filename + ".csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')

        writer.writerows([["location", "latitude", "longitude", "grid_index"], metadata])   #write header of csv-file
        writer.writerows([[], prec_heigths[0]])

        for i, heigth in enumerate(prec_heigths[1:]):       #write all heights combined with duration
            writer.writerow([duration[i]] + heigth)
        


def main(location: str, return_period=None):
    """Extracts precipitation heights from KOSTRA-data and saves it"""
    coords = get_coords(location)               #get coordinates for location
    grid = get_grid_index(coords)               #get number of right grid field
    heights = get_precipitation_heights(grid, return_period)   #extract precipitation heights
    metadata = (location, coords[0], coords[1], grid)

    save_precipitation_heights(location.replace(" ", ""), heights, metadata)    #save heights and metadata to a csv-file



if __name__ == "__main__":
    location = input("Location: ")
    return_period = int(input("Return period: "))

    main(location, return_period)
    
    print(f"csv.file saved to {location.replace(' ', '')}")