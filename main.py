# Author: ZonoN
# Version: 1.0.0
# Discord: ZonoN#9080

from __future__ import print_function

import json
import time

import requests #dependency

from datetime import datetime
from binance.client import Client

import os.path


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import threading

# CONFIGURATION

#DISCORD
webhook = "WEBHOOK_DISCORD" #<-------------------------- PUT

#Binance
api_key = "KEY_BINANCE" #<-------------------------- PUT
api_secret = "SECRET_BINANCE" #<-------------------------- PUT

syncro_time= 50.0




client = Client(api_key, api_secret)
table = []




def init():
    threading.Timer(syncro_time, init).start()

    try:

        with open('orders_to_send.json','w') as file:
            file.write('{"orders": []}')
        time.sleep(2)
                
        openOrders = client.get_open_orders()
        for i in openOrders:

            
            data = json.dumps(i)
            data_dic = json.loads(data)


            time_sell = data_dic['time']
            symbol_sell = data_dic['symbol']
            side_sell = data_dic['side']
            origQty_sell = data_dic['origQty']
            price_sell = data_dic['price']

            order_id = data_dic['orderId']
            

            time_sell = str(time_sell)
            time_sell = time_sell[:-3]
            time_sell = int(time_sell)




            orders = client.get_all_orders(symbol=symbol_sell, limit=2)

            
            
            for z in orders:
                data2 = json.dumps(z)
                data_dic2 = json.loads(data2)

                Qtybuy = data_dic2['origQty']
                
                if Qtybuy == origQty_sell:
                    time_buy = data_dic2['time']
                    buy_order = client.get_my_trades(symbol=symbol_sell,orderId=data_dic2['orderId'])
                    for u in buy_order:

                        price_buy = u['price']

                        new = {
                            order_id:{
                            "date": time_sell,
                                    "orderId": order_id,
                                    "symbol": symbol_sell,
                                    "Quantity": Qtybuy,
                                    "Buy": price_buy,
                                    "Sell": price_sell}
                                    }

                        with open('history_orders.json','r+') as file:
                            # First we load existing data into a dict.
                            file_data = json.load(file)
                            test = str(file_data)
                            timestr = str(time_sell)
                            if(timestr not in test):
                                file_data['orders'].append(new)
                                # Sets file's current position at offset.
                                file.seek(0)
                                # convert back to json.
                                json.dump(file_data, file, indent = 4)

                                with open('orders_to_send.json','r+') as file:
                                    file_data = json.load(file)
                                    file_data['orders'].append(new)
                                    # Sets file's current position at offset.
                                    file.seek(0)
                                    # convert back to json.
                                    json.dump(file_data, file, indent = 4)


        f = open ('orders_to_send.json', "r")
        send_data = json.loads(f.read())

        print("----Nouvelle Synchronisation----")

        for i in send_data['orders']:
            for z in i:
                dic = i[z]

                date_time = int(dic['date'])
                dt_object = datetime.fromtimestamp(date_time)
                dt_object = str(dt_object)
                quantite=float(dic['Quantity'])
                buy=float(dic['Buy'])
                sell=float(dic['Sell'])
                F=quantite*buy
                H=quantite*sell
                buy_max = buy+(buy*0.005)
                #H='=SOMMEPROD((K11=VRAI),%f)' % (G_E)
                print("Ajout d'un nouvel order")
                data = {
                }
                data["embeds"] = [{
                "title" : "🪙 NOUVEAU CALL CRYPTO",
                "description": "🔤 **Symbole**ㅤㅤㅤㅤ📅** Date**\n%sㅤㅤㅤㅤ%s" %(dic['symbol'],dt_object),
                "color": 3066993,
                "fields": [
                {
                    "name": "📥 BUY conseillé",
                    "value": "%.10f BTC" % (buy),
                    "inline": True
                },
                {
                    "name": "📥 BUY maximum",
                    "value": "%.10f BTC" % (buy_max),
                    "inline": True
                },
                {
                    "name": "📤 SELL",
                    "value": "%.10f BTC" % (sell),
                    "inline": True
                },
                {
                    "name": "💵 MISE",
                    "value": "15% Max du Wallet",

                }
                ],
                "thumbnail": {"url": ""},
                "footer": {"text": "⚠️ Nous avons aucune responsabilité sur vos investissements ! ⚠️",
                },
                }]
                result = requests.post(webhook, json = data)
                print("Payload delivered successfully on discord, code {}.".format(result.status_code))

    except Exception as e:
        print("Something went wrong: %s"%(e))

init()
