import requests
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
import json
import pandas as pd
import matplotlib.pyplot as plt


plt.style.use('seaborn-darkgrid')
def get_agreeance_text(ratio):
    if ratio > 3:
        return "absolutely agrees"
    elif 2 < ratio <= 3:
        return "strongly agrees"
    elif 1.5 < ratio <= 2:
        return "agrees"
    elif 1 < ratio <= 1.5:
        return "somewhat agrees"
    elif ratio == 1:
        return "neutral"
    elif 0.67 < ratio < 1:
        return "somewhat disagrees"
    elif 0.5 < ratio <= 0.67:
        return "disagrees"
    elif 0.33 < ratio <= 0.5:
        return "strongly disagrees"
    elif ratio <= 0.33:
        return "absolutely disagrees"
    else:
        return None

pages = [
    'https://www.allsides.com/media-bias/media-bias-ratings',
    'https://www.allsides.com/media-bias/media-bias-ratings?page=1',
    'https://www.allsides.com/media-bias/media-bias-ratings?page=2'
]

data = []

for page in pages:
    r = requests.get(page)
    soup = BeautifulSoup(r.content, "html.parser")

    rows = soup.select('tbody tr')

    for row in rows:
        d = dict()
        d['name'] = row.select_one('.source-title').text.strip()
        d['allsides_page'] = 'https://www.allsides.com' + row.select_one('.source-title a')['href']
        d['bias'] = row.select_one('.views-field-field-bias-image a')['href'].split('/')[-1]
        d['agree'] = int(row.select_one('.agree').text)
        d['disagree'] = int(row.select_one('.disagree').text)
        d['agree_ratio'] = d['agree'] / d['disagree']
        d['agreeance_text'] = get_agreeance_text(d['agree_ratio'])
        data.append(d)

for d in tqdm(data):
    r = requests.get(d['allsides_page'])
    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        website = soup.select_one('.www')['href']
        d['website'] = website
    except TypeError:
        pass

sleep(10)

with open('allsides.json', 'w') as f:
    json.dump(data, f)

df = pd.read_json(open('allsides.json', 'r'))
df.set_index('name', inplace=True)
df.head()
df[df['agreeance_text'] == 'strongly disagrees']
df['total_votes'] = df['agree'] + df['disagree']
df.sort_values('total_votes', ascending=False, inplace=True)
df.head(10)
df2 = df.head(25).copy()
df2.head()

fig, ax = plt.subplots(figsize=(20, 10))

ax.bar(df2.index, df2['agree'], color='#5DAF83')
ax.bar(df2.index, df2['disagree'], bottom=df2['agree'], color='#AF3B3B')

ax.set_ylabel = 'Total feedback'

plt.yticks(fontsize='x-large')
plt.xticks(rotation=60, ha='right', fontsize='x-large', rotation_mode='anchor')

plt.legend(['Agree', 'Disagree'], fontsize='xx-large')
plt.title('AllSides Bias Rating vs. Community Feedback', fontsize='xx-large')
plt.show()