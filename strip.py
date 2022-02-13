import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
from tqdm import tqdm

from utils import *

# https://documenter.getpostman.com/


### ABu Dhabi ###

# querying drivers
drivers = get_drivers()

drivers_list = []
times = []
for lap in tqdm(range(59)):
    url = f"http://ergast.com/api/f1/2021/22/laps/{lap}"
    soup = get_soup(url)
    for time in soup.find_all('timing'):
        splitted = time['time'].split(':')
        parsed = float(splitted[0]) * 60 + float(splitted[1])
        driver = time['driverid'] 

        times.append(parsed)
        drivers_list.append(driver)

df = pd.DataFrame({'time':times, 'driver': drivers_list})

driver_codes = ['HAM', 'VER', 'PER', 'SAI', 'NOR', 'LEC', 'TSU', 'BOT', 'OCO', 'RIC', 'ALO', 'GAS', 'GIO', 'STR', 'VET', 'LAT', 'RAI', 'MSC', 'RUS']
driver_name_to_code = {df['driver'].values[i]: driver for i, driver in enumerate(driver_codes)}
df['driver'] = df['driver'].map(driver_name_to_code)

top10 = ['VER', 'HAM', 'SAI', 'TSU', 'GAS', 'BOT', 'NOR', 'ALO', 'OCO', 'LEC']
filtered = df[(df['driver'].isin(top10)) & (df['time']<95)]
filtered = pd.merge(filtered, drivers, left_on='driver', right_index=True)

f, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10), sharex=True)
sns.stripplot(x='driver', y='time', data=filtered, ax=ax, order=top10, hue='constructor', palette=colormap, s=6)
f, ax = apply_colorscheme(f, ax)