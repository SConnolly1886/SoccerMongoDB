from bs4 import BeautifulSoup
from textwrap import wrap
import re
import requests
import pandas as pd
import pymongo
import json


class TerminalColours:
    HEADER = '\033[95m'   # light magenta
    OKBLUE = '\033[94m'  # light blue
    WIN = '\033[92m'  # light # light green
    DRAW = '\033[93m'  # light yellow
    LOSS = '\033[91m'   # light red
    ERROR = '\033[31m'  # red
    ENDC = '\033[0m'  # reset
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    BLACK = '\033[30m'


def inputCountry(msg):
    while True:
        try:
            L = int(input(msg))
        except ValueError:
            print(f'{TerminalColours.ERROR}**ERROR** Select (1 to 12) only{TerminalColours.ENDC}')
            continue
        except TypeError:
            print(f'{TerminalColours.ERROR}**ERROR** Select (1 to 12) only{TerminalColours.ENDC}')
            continue
        if 1 <= L <= 11:
            return L
        if L == 12:
            quit()
        else:
            print(f'{TerminalColours.ERROR}**ERROR** Select (1 to 12) only{TerminalColours.ENDC}')


# prompting for which country.
country = inputCountry(f'\nSelect which nations league(s) you would like to store in a MongoDB database:\n\n1) England\n2) Scotland\n3) Germany\n4) Italy\n5) Spain\n6) France\n7) Netherlands\n8) Belgium\n9) Portugal\n10) Turkey\n11) Greece\n12) Leave Program\n{TerminalColours.ENDC}')


def country_select(country):
    if country == 1:
        name = 'England'
    if country == 2:
        name = 'Scotland'
    if country == 3:
        name = 'Germany'
    if country == 4:
        name = 'Italy'
    if country == 5:
        name = 'Spain'
    if country == 6:
        name = 'France'
    if country == 7:
        name = 'Netherlands'
    if country == 8:
        name = 'Belgium'
    if country == 9:
        name = 'Portugal'
    if country == 10:
        name = 'Turkey'
    if country == 11:
        name = 'Greece'
    return name


url_country = country_select(country)
# set country to lower+m, needed for url
url_cc = f'{url_country}m'.lower()

print(f'{TerminalColours.WIN} --Downloading Files from http://www.football-data.co.uk/-- {TerminalColours.ENDC}')
print(f'Country:\t{TerminalColours.WIN} --{url_country}-- {TerminalColours.ENDC}')

# website with football data, no api required
starting_url = "http://www.football-data.co.uk/"

r = requests.get(starting_url + url_cc)

# read/parses the cocntents of the html page
soup = BeautifulSoup(r.content, features='lxml')

allsearch = ''

# reading all the links on the selected page.
for link in soup.find_all('a'):
    mysearch = link.get('href')
    allsearch = allsearch+' '+mysearch

# spliting to get the array of the strings.
y = allsearch.split()

# extracting only csvs using re. Creating list of all csv files
z = [list(x for x in y if re.search('^mmz.*.*.csv$', str(x)))]

# indexing to get back the list from list of list.
z = z[0]

# creating the base url.
base_url = 'http://www.football-data.co.uk/'

# creating an empty list to append / update with data as we read.
complete_url = []

# converting the abstract links to primary form so that they can be read.
for i in (z):
    u = base_url + str(i)
    complete_url.append(u)

arrows = f'{TerminalColours.OKBLUE}------------->{TerminalColours.ENDC}'

# use pandas to create dataframe. Easy to convert pd to json (mongodb)

readings = pd.DataFrame()
for m in complete_url:
    # split each url. need to get years.
    http, slash, www, mmz, years, div = m.split('/')
    sy, ey = wrap(years, 2)
    # put forward slash to separate the season years
    seez = f'{sy}/{ey}'
    ''' encoding ='latin1' means that dev tools are sourcing the files as latin1 instead of the UTF-8 files that they are. This happens irrespective of the Encoding: UTF-8.'''
    try:
        reader = pd.read_csv(m, sep=',', encoding='latin1', engine='python')
    except:
        # use index_col=False to avoid errors, deals with trailing commas as error_bad_lines=False will remove offending rows
        reader = pd.read_csv(m, sep=',', encoding='latin1', engine='python', index_col=False)
    # reader = pd.read_csv(m, sep=',', error_bad_lines=False, warn_bad_lines=False, encoding='latin1')
    print(f'{arrows}{m}')
    # insert new column in pd, after div
    reader.insert(1, 'Season', '')
    # use years split taken from links
    reader['Season'] = seez
    # print(reader)
    # change Division (ex E0) to name (ex Premier League)
    reader.loc[(reader.Div == 'E0'), 'Div'] = 'Premier League'  # England 1
    reader.loc[(reader.Div == 'E1'), 'Div'] = 'Championship'  # England 2
    reader.loc[(reader.Div == 'E2'), 'Div'] = 'League 1'  # England 3
    reader.loc[(reader.Div == 'E3'), 'Div'] = 'League 2'  # England 4
    reader.loc[(reader.Div == 'EC'), 'Div'] = 'Conference'  # England 5
    reader.loc[(reader.Div == 'SC0'), 'Div'] = 'Premier League'  # Scotland 1
    reader.loc[(reader.Div == 'SC1'), 'Div'] = 'Division 1'  # Scotland 2
    reader.loc[(reader.Div == 'SC2'), 'Div'] = 'Division 2'  # Scotland 3
    reader.loc[(reader.Div == 'SC3'), 'Div'] = 'Division 3'  # Scotland 4
    reader.loc[(reader.Div == 'D1'), 'Div'] = 'Bundesliga'  # Germany 1
    reader.loc[(reader.Div == 'D2'), 'Div'] = '2 Bundesliga'  # Germany 2
    reader.loc[(reader.Div == 'I1'), 'Div'] = 'Serie A'  # Italy 1
    reader.loc[(reader.Div == 'I2'), 'Div'] = 'Serie B'  # Italy 2
    reader.loc[(reader.Div == 'SP1'), 'Div'] = 'La Liga'  # Spain 1
    reader.loc[(reader.Div == 'SP2'), 'Div'] = 'Segunda Division'  # Spain 2
    reader.loc[(reader.Div == 'F1'), 'Div'] = 'Ligue 1'  # France 1
    reader.loc[(reader.Div == 'F2'), 'Div'] = 'Ligue 2'  # France 2
    reader.loc[(reader.Div == 'N1'), 'Div'] = 'Eredivisie'  # Netherlands
    reader.loc[(reader.Div == 'B1'), 'Div'] = 'First Division A'  # Belgium
    reader.loc[(reader.Div == 'P1'), 'Div'] = 'Primeira Liga'  # Portugal
    reader.loc[(reader.Div == 'T1'), 'Div'] = 'Super Lig'  # Turkey
    reader.loc[(reader.Div == 'G1'), 'Div'] = 'Super League'  # Greece
    readings = readings.append(reader)

# renaming some of the column names as required (No '.' in column headerss)
readings.columns = readings.columns.str.replace('[.]', '_')

# convert dates. Date formats vary. This sets the standard. Removing dt.strftime will result in datetime64 which will convert to timestamp(json)
readings['Date'] = pd.to_datetime(readings['Date']).dt.strftime('%Y-%m-%d')

# Localhost connection at port `27017`.

client = pymongo.MongoClient('mongodb://localhost:27017/')

# create Socccer db. Collections will be by country
db = client['Soccer']

# set collection to country selection
collections = db[url_country]

# convert pd to json, then remove empty lists (Data varies year to year, country to country)
data_json = json.loads(readings.to_json(orient='records'))


def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}


json_mongo = remove_empty_elements(data_json)

# insert into mongodb
collections.insert_many(json_mongo)

arrows = f'{TerminalColours.OKBLUE}------------->{TerminalColours.ENDC}'

# print country selected
print(f"\n{TerminalColours.UNDERLINE}Uploaded to MongoDB {TerminalColours.WIN}'Soccer'{TerminalColours.ENDC} Database:{TerminalColours.ENDC}\nCollection Created: \n{arrows}{TerminalColours.WIN}{url_country}{TerminalColours.ENDC}\n")
