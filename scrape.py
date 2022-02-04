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


url = f"http://ergast.com/api/f1/2021/drivers"
payload={}
headers = {}

# querying drivers
response = requests.request("GET", url, headers=headers, data=payload)

soup = BS(response.content, 'html.parser')
id = []
for driver in soup.find_all('driver'):
    id.append(driver['code'])

drivers = pd.DataFrame(index=id)
drivers['constructor'] = ['Alpine', 'Mercedes', 'AlphaTauri', 'Alfa Romeo', 'Mercedes', 'Williams', 'Williams', 'Ferrari', 'Haas', 'McLaren', 'Alpine', 'Red Bull',
'Alfa Romeo', 'McLaren', 'Williams', 'Ferrari', 'Haas', 'Aston Martin', 'AlphaTauri', 'Red Bull', 'Aston Martin' ]
drivers['color'] = drivers['constructor'].map(colormap)

print('*** querying race results ***')

results = drivers.copy()
results = results.drop(['color','constructor'], axis=1)

for i in range(1,23):
    url = f"http://ergast.com/api/f1/2021/{i}/results"
    response = requests.request("GET", url, headers=headers, data=payload)

    soup = BS(response.content, 'html.parser')
    racename = soup.find('racename').text
    print(f'processing {racename}')

    flag = True
    temp = {}
    for result in soup.find_all("result"):
        position = result['position']
        temp[result.find('driver')['code']] = int(position)

        #dealing with dnf
        if flag:
            number_of_laps = int(result.find('laps').text)
            flag = False
        else:
            laps_completed = int(result.find('laps').text)
            if laps_completed + 2 < number_of_laps:

                temp[result.find('driver')['code']] = np.NaN
    
    race = pd.Series(list(temp.values()), index=list(temp.keys()))
    results[racename] = race


print('*** querying qualifying results ***')

quali = drivers.copy()
quali = quali.drop(['color','constructor'], axis=1)

for i in range(1,23):
    url = f"http://ergast.com/api/f1/2021/{i}/qualifying"
    response = requests.request("GET", url, headers=headers, data=payload)

    soup = BS(response.content, 'html.parser')
    temp = {}
    racename = soup.find('racename').text
    print(f'processing {racename}')

    for result in soup.find_all('qualifyingresult'):
        position = result['position']
        temp[result.find('driver')['code']] = int(position)
    race = pd.Series(list(temp.values()), index=list(temp.keys()))
    quali[racename] = race
    
# compute average positions    
drivers['quali'] = quali.mean(axis=1)
drivers['race'] = results.mean(axis=1)

#plotting results
f, ax = plt.subplots(figsize=(10,10))
sns.scatterplot(x='quali', y='race', data=drivers, hue='constructor', palette=colormap, ax=ax, s=60)

# making plot pretty
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
ax.grid(alpha=0.1)
ax.get_legend().remove()
ax.set_xlabel('Average Qualifying Results', weight='bold')
ax.set_ylabel('Average Race Results', weight='bold')
ax.set_xticks([2,4,6,8,10,12,14,16,18,20])
ax.set_yticks([2,4,6,8,10,12,14,16,18,20])

# dealing with overlapping labels
labels = ax.get_xticklabels() + ax.get_yticklabels()
for label in labels:
        label.set_fontweight('bold') 
for _, driver in drivers.iterrows():
        if driver.name == 'LEC':
                ax.text(driver['quali']-.9, driver['race']+.05, str(driver.name), color='white',weight='bold')
        elif driver.name == 'PER':
                ax.text(driver['quali']+.05, driver['race']-.5, str(driver.name), color='white',weight='bold')   
        elif driver.name == 'ALO':
                ax.text(driver['quali']-.6, driver['race']-.5, str(driver.name), color='white', weight='bold') 
        else:
                ax.text(driver['quali']+.1, driver['race']+.1, str(driver.name), color='white', weight='bold')
plt.rcParams.update({'font.size': 12})

print('*** saving figure ***')
plt.savefig('scatter.png', dpi=1000)



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



drivers = []
times = []
for lap in tqdm(range(59)):
    url = f"http://ergast.com/api/f1/2021/22/laps/{lap}"
    soup = get_soup(url)
    for time in soup.find_all('timing'):
        splitted = time['time'].split(':')
        parsed = float(splitted[0]) * 60 + float(splitted[1])
        temp.append(parsed) 
        driver = time['driverid'] 

        times.append(parsed)
        drivers.append(driver)

df = pd.DataFrame({'time':times, 'driver': drivers})

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
ax.set_yticklabels(['1:24','1:26','1:28','1:30','1:32','1:34'])