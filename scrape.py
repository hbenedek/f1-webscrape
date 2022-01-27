import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

