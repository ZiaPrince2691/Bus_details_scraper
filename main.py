import time

from book_me_functions import *

dep   = input('  Departure : ')
arr   = input('Destination : ')
date  = input('       Date : ')
month = input('      Month : ')

time.sleep(5)

url = "https://bookme.pk/"

# GETTING PAGE SOURCE USING SELENIUM

html = get_page_source(url, dep, arr, date, month)

# SCRAPING DATA FROM PAGE SOURCE

df_buses = get_bus_details(html)

# CREATING FILES

create_files(df_buses)