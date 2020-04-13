from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import json
import time
import configparser
import logging

import telegram
from telegram import ParseMode
from telegram.ext import Dispatcher, MessageHandler, Filters

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

while (True):
    
    driver.get("https://www.ozbargain.com.au/cat/electrical-electronics/deals")
    htmltext = driver.page_source
    driver.close()

    soup = BeautifulSoup(htmltext, 'html.parser')
    deals_divs = soup.findAll("div", {"class": "node-ozbdeal"})
    bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))

    new_deals = []
    update = False
    with open('data.txt') as json_file:
        pre_data = json.load(json_file)
        tmp_data = [p['id'] for p in pre_data['deals']]


    for i,deal in enumerate(deals_divs):
        if i >= 10:
            break
        else:
            h2 = deal.find('h2')
            deal_id = h2['id'].replace('title','')

            if deal_id not in tmp_data:
                update = True
                new_deals.append(deal_id)
                title = h2['data-title']
                bot.send_message(
                    chat_id=(config['TELEGRAM']['CHAR_ID']), 
                    text="<>"title,
                    parse_mode=telegram.ParseMode.HTML
                )

    if update:
        for deal in new_deals:
            pre_data['deals'].insert(0,{'id':deal})
            pre_data['deals'].pop()

        with open('data.txt', 'w') as outfile:
            json.dump(pre_data, outfile)
            
    time.sleep(600)

    
