from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sqlite3
import time
import os

def load_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")    # Open in incognito mode

    service = Service(r'C:\Program Files (x86)\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_loading(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "originCity")),
        EC.presence_of_element_located((By.ID, "destinationCity")),
    )

def set_departure(driver , dep):
    try:
        departure_element = driver.find_element(By.ID , 'originCity')
        departure_element.click()

        departure = driver.find_element(By.XPATH, '//*[@placeholder="From"]')
        departure.send_keys(dep.title())
        departure.send_keys(Keys.RETURN)
    except:
        print("Can't find Departure")

def set_arival(driver , arr):
    try:
        arival_element = driver.find_element(By.ID , 'destinationCity')
        arival_element.click()

        arival = driver.find_element(By.XPATH, '//*[@placeholder="To"]')
        arival.send_keys(arr.title())
        arival.send_keys(Keys.RETURN)
    except:
        print("Can't find Arival")

def set_date(driver , date , month):
    try:
        date_element = driver.find_element(By.XPATH, '//*[@placeholder="Departure Date"]')
        date_element.click()

        month_element = driver.find_element(By.XPATH, '//div[@class="dp__month_year_select" and @aria-label="Open months overlay"]')
        month_element.click()

        month = driver.find_element(By.XPATH, f'//div[@class="dp__overlay_col" and @aria-disabled="false" and @data-test="{month.title()}"]')
        month.click()

        date = driver.find_element(By.XPATH , f'//div[@class="dp__calendar_item" and @aria-disabled="false"]//div[@class="dp__cell_inner dp__pointer dp__date_hover" and text()={date}]')
        date.click()

    except:
        print("Can't find Date")

def submit(driver):
    try:
        submit_element = driver.find_element(By.XPATH, '//*[@type="submit" and @class ="btn btn-secondary text-white w-100"]')
        submit_element.click()
    except:
        print("Can't find Submit")

def get_page_source(url, dep, arr, date, month):
    driver = load_driver()
    driver.get(url)
    wait_for_loading(driver)
    set_departure(driver, dep)
    set_arival(driver, arr)
    set_date(driver, date, month)
    submit(driver)
    time.sleep(5)
    html = driver.page_source
    print('Page Source loaded Successfully!')
    driver.quit()
    return html

def get_bus_details(html):
    seats_left   = []
    timings      = []
    prices       = []
    bus_services = []
    cruise_types = []

    soup = BeautifulSoup(html, 'html.parser')
    buses = soup.find_all('div' , class_ = 'detail-card card my-3 text-reset')
    durations = soup.find_all('div' , class_ = 'duration text-end')

    for duration in durations:
        seats = duration.find('p' , class_ = 'mb-0')
        timing = duration.find('h5' , class_ = 'font-weight-600 mb-0')
        timings.append(timing.text)
        
        if seats:
            seats_left.append(seats.text.split()[0])
        else:
            seats_left.append(np.nan)

    price_elements = soup.find_all('h5' , class_ = 'font-weight-600 mb-0 fs-5 mx-2 me-3')

    for price_element in price_elements:
        price = price_element.find('span').text
        price = price.replace('Rs' , '')
        price = price.replace(',' , '')
        prices.append(int(price))

    bus_elements = soup.find_all('div' , class_ = 'd-flex justify-content-between align-items-center')

    for bus_element in bus_elements:
        cruise_type = bus_element.find('span').text
        bus_service = bus_element.find('h5' , class_ = 'font-weight-600 mb-0').text.replace(cruise_type , '')
        bus_services.append(bus_service.strip())
        cruise_types.append(cruise_type)

    dict_buses = {
        'Bus_Service' : bus_services,
        'Cruise_Type' : cruise_types,
        'Timing' : timings,
        'Seat_Left' : seats_left,
        'Price' : prices
    }

    df_buses = pd.DataFrame(dict_buses)
    print(df_buses.head())
    return df_buses

def create_files(df):
    con = sqlite3.connect('Buses.db')
    cursor_obj = con.cursor()

    df.to_sql('Buses' , con=con , if_exists='replace' , index = False)
    bus_services = ['Road Master Bus' , 'Silk Line' , 'Daewoo Express' , 'Al Makkah' , 'Rajput Travels Rathore Group']

    for bus_service in bus_services:
        query = f"""SELECT * FROM Buses where Bus_Service = '{bus_service}'"""
        df = pd.read_sql(query, con=con)
        # df.to_csv(f'{bus_service}.csv')

        # Define the directory and file path
        directory = "Bus_services"
        file_path = os.path.join(directory, f'{bus_service}.csv')

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the DataFrame to a CSV file in the directory
        df.to_csv(file_path, index=False)
        print(f"File saved to {file_path}")