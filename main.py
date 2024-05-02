import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

current_page = 1
proceed = True
dataList = []
date_pattern = r'Updated (\d{2} \w{3} \d{4}), Added (\d{2} \w{3} \d{4})'

while proceed:
    print("Currently scraping page " + str(current_page))
    url = "https://www.propertypro.ng/property-for-rent/in/lagos?page=" + str(current_page)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    title = ''
    price = ''
    location = ''
    pid = ''
    status = []
    bedroom = ''
    bathroom = ''
    toilet = ''
    date_added = ''
    date_updated = ''

    div_jumbotron = soup.find('div', class_='jumbotron')
    if div_jumbotron:
        p_tag = div_jumbotron.find('p', class_='text-center', style='font-size: 20px;')
        if p_tag:
            print(p_tag.text)
            proceed = False
    else:
        all_properties = soup.find_all('div', class_='single-room-sale listings-property')
        for house_property in all_properties:
            property_title = house_property.find('h3', class_='listings-property-title2')
            # Name of the property
            property_image_div = house_property.find('div', class_='single-room-img')
            if property_image_div:
                property_image_alt = property_image_div.find('img').attrs['alt']
                title = property_image_alt
                # print(property_image_alt)
            # price of the property
            property_price_div = house_property.find('div', class_='single-room-text')
            if property_price_div:
                price_text = property_price_div.find('h3').text
                if price_text:
                    price = price_text[2:]
                    # print(price[2:])
            # PID of the property
            single_room_text = house_property.find('div', class_='single-room-text')
            if single_room_text:
                pid_after_element = single_room_text.find('div', class_='furnished-btn')
                if pid_after_element:
                    pid_element = pid_after_element.find_previous_sibling()
                    if pid_element:
                        pid = pid_element.text[5:]
                        # print(pid[5:])
            # location of the property
            single_room_text = house_property.find('div', class_='single-room-text')
            if single_room_text:
                a_tag_before_location = single_room_text.find('a')
                if a_tag_before_location:
                    location_text = a_tag_before_location.find_next_sibling()
                    location = location_text.text
                    # print(location_text)
            # bedroom, bathroom and toilet
            single_room_text = house_property.find('div', class_='single-room-text')
            if single_room_text:
                room_nums = single_room_text.find('div', class_='fur-areea')
                if room_nums:
                    bedroom_span = room_nums.find('span')
                    if bedroom_span:
                        bedroom = bedroom_span.text[0]
                        # print(bedroom)
                        bathroom_span = bedroom_span.find_next_sibling()
                        if bathroom_span:
                            bathroom = bathroom_span.text[0]
                            # print(bathroom)
                            toilet_span = bathroom_span.find_next_sibling()
                            if toilet_span:
                                toilet = toilet_span.text[0]
                                # print(toilet)
            # status of the property
            single_room_text = house_property.find('div', class_='single-room-text')
            status_texts = []
            if single_room_text:
                status_tag = single_room_text.find('div', class_='furnished-btn')
                if status_tag:
                    a_tags = status_tag.find_all('a')
                status_texts = [a_tag.text for a_tag in a_tags]
            status_text = ' ,'.join(status_texts)
            status = status_text
            # print(status)

            # date added and date updated
            single_room_text = house_property.find('div', class_='single-room-text')
            if single_room_text:
                date_tag = single_room_text.find('h5')
                if date_tag:
                    date_string = date_tag.text
                    # print(date_string)
                    match = re.search(date_pattern, date_string)
                    if match:
                        date_updated = match.group(1)
                        date_added = match.group(2)
            # print(date_added)
            item = {
                'Title': title,
                'Price': price,
                'PID': pid,
                'Location': location,
                'Bedroom': bedroom,
                'Bathroom': bathroom,
                'Toilet': toilet,
                'Status': status,
                'Date Added': date_added,
                'Date Updated': date_updated
            }
            dataList.append(item)
        current_page += 1

df = pd.DataFrame(dataList)
os.makedirs('data_set', exist_ok=True)
df.to_csv('data_set/house_lagos_data_set.csv')
