import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt

from utils import *

# querying Hungaroring laptimes between 2010-2021
times = defaultdict(list)

for year in range(2010,2022):
    print(year)
    url = f"http://ergast.com/api/f1/{year}/circuits"
    soup = get_soup(url)
    N = len(soup.find_all('circuitname'))

    for race in range(1,N+1):
        url = f"http://ergast.com/api/f1/{year}/{race}/laps/1"
        soup = get_soup(url)

        if soup.find('racename').text == 'Hungarian Grand Prix':
            temp = []
            for lap in tqdm(range(70)):
                url = f"http://ergast.com/api/f1/{year}/{race}/laps/{lap}"
                soup = get_soup(url)
                

                for time in soup.find_all('timing'):
                    splitted = time['time'].split(':')
                    parsed = float(splitted[0]) * 60 + float(splitted[1])
                    temp.append(parsed)
                    
            times[year] = temp
            

# storing the data
df = pd.DataFrame()
data = 0
for k,v in times.items():
    data = data + len(v)
    new = pd.DataFrame({'time': v, 'year': k})
    df = pd.concat([df, new], axis=0)

new_index = [i for i in range(data)]
df.index = new_index

# excluding laps more than 2 mins (pitstops/safety cars, rain?)
filtered = df[df['time'] < 120]

#plotting the results
f, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10), sharex=True)
sns.pointplot(data=filtered, x="year", y="time", ci=0, color='white', size=10)
sns.pointplot(data=filtered, x="year", y="time", err_style="band", ci=99, linewidth=30 ,errwidth=3, color='#00D2BE', join=False)

f, ax = apply_coloscheme(f, ax)
ax.set_title('Hungaroring Average Race Pace (with 99% CI)', color='white', weight='bold')
ax.set_xlabel('year', weight='bold')
ax.set_ylabel('Laptime', weight='bold')
ax.set_yticklabels(['1:22','1:24','1:26','1:28','1:30','1:32','1:34','1:36'])