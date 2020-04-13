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
                chat_id=(config['TELEGRAM']['CHART_ID']), 
                text=title
            )

if update:
    for deal in new_deals:
        pre_data['deals'].insert(0,{'id':deal})
        pre_data['deals'].pop()

    with open('data.txt', 'w') as outfile:
        json.dump(pre_data, outfile)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'


def reply_handler(bot, update):
    """Reply message."""
    text = update.message.text
    if text == 'FeedMe':
        update.message.reply_text("Start Feeding")
    else:
        newText = '<b>Try other key words</b>'
        #newText = '<b>Try Again</b> <i>italic</i> <a href="http://google.com">link</a>.'

        update.message.reply_text(newText,parse_mode=telegram.ParseMode.HTML)


# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)

