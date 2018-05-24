# -*- coding: UTF-8 -*-
import requests
import time
import urlparse
from datetime import datetime
from config import config
from models.models import TradingPair, s


def check():
    try:
        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Requesting a list of trading pairs...')
        r = requests.get(config.TRADING_PAIRS_LIST)
        response = []
        r = r.json()
        for rl in r['data']:
            response.append(rl['symbol'])

        return response
    except requests.exceptions.RequestException as e:
        print e
    except IOError as ioe:
        print ioe
    return None
    
    
def compare(data):
    print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Comparing the list with local database...')
    listOfPairs = []
    
    first_run = True if s.query(TradingPair).count() == 0 else False
    
    for r in data:
        tradingPair = s.query(TradingPair).filter(TradingPair.name == r)
        if tradingPair.count():
            tradingPair.first().update_timestamp()
        else:
            listOfPairs.append(TradingPair(r))

    if listOfPairs:
        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Number of new pairs: ' + str(len(listOfPairs)))
        s.add_all(listOfPairs)
        if first_run == False:
            notify(listOfPairs)
    
    s.commit()
    
    
def notify(listings):
    try:
        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Sending a notification via email')
        requests.post(
            config.SANDBOX,
            auth=("api", config.AUTH),
            data={"from": config.FROM,
                  "to": config.EMAIL,
                  "subject": "[BINANCE ALERT] New listings",
                  'html': '<html>' + '<br>'.join(['<strong>' + p.name + '</strong> - ' + p.created_at.strftime('Added on: %d.%m.%Y - %H:%M:%S') for p in listings]) + '</html>'})
        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Notification sent')
        
        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Sending a message to Telegram channel')
        
        for l in listings:
            
            t = '%F0%9F%94%94 %F0%9F%94%94 %F0%9F%94%94' + ' *New Binance listing %F0%9F%94%94 %F0%9F%94%94 %F0%9F%94%94\n\r' + l.name  + '* - ' + l.created_at.strftime('Added on: %d.%m.%Y - %H:%M:%S')
            requests.get('https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}&parse_mode={3}'.format(config.BOT_KEY, config.CHANNEL_ID, t, 'markdown'))

        print(datetime.now().strftime('[%d.%m.%Y - %H:%M:%S] - ') + 'Message(s) sent to subscribers')
        
        
    except requests.exceptions.RequestException as e:
        print e
        time.sleep(config.INTERVAL * 60)
        notify(listings)

def start(interval=config.INTERVAL):
    while True:
        try:
            data = check()
            if data:
            	compare(data)
        except KeyboardInterrupt:  
            print('Application stopped by user')
            break
        except Exception as e:
            print(e)
        time.sleep(interval*60)

start()