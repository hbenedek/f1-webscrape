import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
from tqdm import tqdm

# https://documenter.getpostman.com/

colormap = {
    'Mercedes':	            '#00D2BE',
    'Ferrari':	            '#DC0000',
    'Red Bull':	            '#0600EF',	
    'Alpine':           	'#0090FF',
    'Haas':	                '#FFFFFF',	
    'Aston Martin':	        '#006F62',	
    'AlphaTauri':	        '#2B4562',	
    'McLaren':	            '#FF8700',
    'Alfa Romeo':       	'#900000',
    'Williams':	            '#005AFF'}	

### ABu Dhabi ###

def time_to_int(time):
    try:
        minute = time.hour
        second = time.minute
        hundredth = time.second
        return minute * 60 * 100 + second * 100 + hundredth
    except:
        return np.NaN

def int_to_time(int_):
    minute = int(int_ / 6000)
    second = int(int(int_ - minute * 6000) /100)
    hundreadth = (int_ - minute * 6000 - second * 100) * 10000
    return dt.time(minute=minute, second=second, microsecond=hundreadth)

def get_soup(url):
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BS(response.content, 'html.parser')
    return soup

# querying drivers
soup = get_soup('http://ergast.com/api/f1/2021/drivers')
id = []
for driver in soup.find_all('driver'):
    id.append(driver['code'])

drivers = pd.DataFrame(index=id)
drivers['constructor'] = ['Alpine', 'Mercedes', 'AlphaTauri', 'Alfa Romeo', 'Mercedes', 'Williams', 'Williams', 'Ferrari', 'Haas', 'McLaren', 'Alpine', 'Red Bull',
'Alfa Romeo', 'McLaren', 'Williams', 'Ferrari', 'Haas', 'Aston Martin', 'AlphaTauri', 'Red Bull', 'Aston Martin' ]
drivers['color'] = drivers['constructor'].map(colormap)

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

ax.get_legend().remove()
background = '#000915' 
f.set_facecolor(background)
ax.set_facecolor(background)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.yaxis.label.set_color('white')
ax.xaxis.label.set_color('white')
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color(background) 
ax.spines['right'].set_color(background)
ax.spines['left'].set_color('white')
ax.grid(alpha=0.2)

ax.set_title('2021 Abu Dhabi GP Laptimes Stripplot', color='white', weight='bold')
ax.set_xlabel('Driver', weight='bold')
ax.set_ylabel('Laptimes', weight='bold')
#ax.set_yticklabels(['1:24','1:26','1:28','1:30','1:32','1:34'])
plt.show()