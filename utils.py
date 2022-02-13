import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
from tqdm import tqdm

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

def apply_colorscheme(f, ax):
    #ax.get_legend().remove()
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
    return f, ax


def bootstrap_CI(data, nbr_draws):
    means = np.zeros(nbr_draws)
    data = np.array(data)

    for n in range(nbr_draws):
        indices = np.random.randint(0, len(data), len(data))
        data_tmp = data[indices] 
        means[n] = np.nanmean(data_tmp)

    return [np.nanpercentile(means, 2.5),np.nanpercentile(means, 97.5)]


def get_drivers():
    url =  "http://ergast.com/api/f1/2021/drivers"
    soup = get_soup(url)
    id = []

    for driver in soup.find_all('driver'):
        id.append(driver['code'])

    drivers = pd.DataFrame(index=id)

    # TODO: fix Kubica
    drivers['constructor'] = ['Alpine', 'Mercedes', 'AlphaTauri', 'Alfa Romeo', 'Mercedes', 'Williams', 'Williams', 'Ferrari', 'Haas', 'McLaren', 'Alpine', 'Red Bull',
    'Alfa Romeo', 'McLaren', 'Williams', 'Ferrari', 'Haas', 'Aston Martin', 'AlphaTauri', 'Red Bull', 'Aston Martin' ]
    drivers['color'] = drivers['constructor'].map(colormap)
    return drivers