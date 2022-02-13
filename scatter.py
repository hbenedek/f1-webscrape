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

print('*** querying race results ***')

drivers = get_drivers()

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
f, ax = apply_colorscheme(f, ax)
# making plot pretty
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



