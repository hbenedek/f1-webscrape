import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt


def get_soup(url):
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BS(response.content, 'html.parser')
    return soup


def bootstrap_CI(data, nbr_draws):
    means = np.zeros(nbr_draws)
    data = np.array(data)

    for n in range(nbr_draws):
        indices = np.random.randint(0, len(data), len(data))
        data_tmp = data[indices] 
        means[n] = np.nanmean(data_tmp)

    return [np.nanpercentile(means, 2.5),np.nanpercentile(means, 97.5)]


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


# calculating average laptimes and bootsrapped confidence intervals
means = []
lower = []
upper = []

for k,v in times.items():
    v = np.array(v)
    v = v[v<130]
    times[k] = v
    means.append(np.mean(v))

    l, u = bootstrap_CI(v, 1000)

    lower.append(l)
    upper.append(u)

df = pd.DataFrame(index=[year for year in range(2010,2022)])
df['mean'] = means
df['lower'] = lower
df['upper'] = upper
df['year'] = df.index


#plotting the results
f, ax = plt.subplots(nrows=1, ncols=1, figsize=(14, 10), sharex=True)
plt.fill_between(x='year', y1='lower', y2='upper', data = df, alpha=.2, color='blue') # where lower/upper bound are array like y1 = df['c1'] - df['c3']
sns.lineplot(x='year', y='mean', data=df, ax=ax, color='blue',marker='o',  markersize=10)