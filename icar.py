import requests
from bs4 import BeautifulSoup
import pandas as pd
import codecs
from urllib.parse import unquote
import time
attr_list = []
base_page = 'https://www.icar.co.il/'
model_name_key='name'
manuf_name_key='manufacture'
first = True
def parse_car_model(page_url, company, cars):
    #print("Parsing car url " + page_url)
    global first
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    attr_val_dict = {}

    if response.status_code == 200:
        model_block = soup.find('h1', class_='d-block version_h1 mt-3')
        modle_name = ''.join(model_block.stripped_strings)
        attr_val_dict[model_name_key] = modle_name
        attr_val_dict[manuf_name_key] = company
        accordion = soup.find_all('div', class_='accordion chart_table')
        for acc in accordion:
            trs = acc.find_all('tr')

            for tr in trs:
                attr_name = tr.get('data-field')
                if first:
                    attr_list.append(attr_name)

                td_tags = tr.find_all('td')
                if len(td_tags) == 2:
                    val = td_tags[1].text
                    if attr_name == 'price':
                        val = "".join([char for char in val if char.isdigit()])
                    val = val.lstrip('\r\n ')
                    val = val.rstrip()
                    attr_val_dict[attr_name] = val

    first = False
    cars.append(attr_val_dict)

def parse_car_page(page_url, company, cars):
    page = base_page + page_url
    response = requests.get(page)
    #print(page)

    model_set= set()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('div', class_='car-version compare_container')
        for row in rows:
            anchor_tags = row.find_all('a')
            for tag in anchor_tags:
                href_value = tag.get('href', '')
                if href_value.startswith('/'):
                    model_set.add(href_value)
        for model_url in model_set:
            parse_car_model(base_page + model_url, company, cars)

    else:
        print("error opening page " + page)
    return 0

# List of target pages
#pages_list = ['https://www.icar.co.il/BYD/']
pages_list = [base_page + '%D7%90%D7%A1%D7%98%D7%95%D7%9F_%D7%9E%D7%A8%D7%98%D7%99%D7%9F/']

# Create an empty list to store extracted data
data_list = []
cars = []

def parse_manufacture(page_url):
    # Fetch the page content

    response = requests.get(page_url)
    tokens = page_url.split('/')
    company = unquote(tokens[-2])

    #continue
    if response.status_code == 200:
        print(company)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('div', class_='row cars manufatures')
        car_models_href_list = []

        for row in rows:
            #print(rows)
            anchor_tags = row.find_all('a')
            for tag in anchor_tags:
                href_value = tag.get('href', '')

                if href_value.startswith('/' + company):
                    #print(f"Found href value: {href_value}")
                    if href_value.count('/') > 3:
                        car_models_href_list.append(href_value)
        car_models_href_set = set(car_models_href_list)
        #print(car_models_href_set)
        for model_url in car_models_href_set:
            parse_car_page(model_url, company, cars)

response = requests.get(base_page)

if response.status_code == 200:
    #time.sleep(20)
    soup = BeautifulSoup(response.content, 'html.parser')

    #rows = soup.find_all('ul', class_='manufacturer_list')
    rows = soup.find_all('div', class_='mainanv d-none d-md-block')

    #print(rows)
    manu_list = []
    #parse_manufacture('https://www.icar.co.il/%D7%95%D7%95%D7%9C%D7%95%D7%95/')

    for row in rows:
        anchor_tags = row.find_all('a')
        for tag in anchor_tags:
            href_value = tag.get('href', '')
            parse_manufacture(base_page + href_value)

else:
    print("error opening " + base_page)
#print(len(attr_list))
j=0

g_keys = set()
for i in cars:
    keys = list(i.keys())
    for key in keys:
        g_keys.add(key)

cars_col = list(g_keys)



main_fields = ['manufacture', 'name', 'price', 'engine', 'power', 'consumption', 'length', 'width', 'height', 'cargo', 'sitting',  'acceleration', 'screen_size']
for field in reversed(main_fields):
    index_to_relocate = cars_col.index(field)
    cars_col.pop(index_to_relocate)
    cars_col.insert(0, field)  # Insert item at index 0

secondary_fields = ['wheel','guarantee', 'airbag', 'launch', 'hotchair', 'sunroof', 'adaptive_cruise_control', 'speed', 'moment', 'wireless_charging', 'autonomous_braking', 'upholstery', 'airconditioning', 'parking_camers', 'automatic_parking', 'ignition', 'doors', 'blind_spot', 'parking_sensors', 'lane_assist', 'pedestrian_identification', 'autochair']
for field in reversed(secondary_fields):
    index_to_relocate = cars_col.index(field)
    cars_col.pop(index_to_relocate)
    cars_col.insert(len(main_fields), field)  # Insert item at index main_fields

cars_values = []
for car in cars:
    values = []
    for key in cars_col:
        if (key in car):
            values.append(car[key])
        else:
            values.append('')
    cars_values.append(values)

df = pd.DataFrame(cars_values, columns=cars_col)
df.to_csv('new_cars_data.csv', index=False, encoding='utf-8-sig')

