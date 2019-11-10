import requests

import pandas as pd
import matplotlib.pyplot as plt



def get_data(date, coin):
    print coin
    #CHANGE HERE 1) histohour gives hourly data and 2) histoday gives daily data. 
    url = "https://min-api.cryptocompare.com/data/histohour?fsym={}&api_key=0881ca839b8a225434bdf776bbb00cc1d51958f9ce3d68fa5185fdab42ee1508&tsym=USD&limit=2000&toTs={}".format(coin, date)
    r = requests.get(url)
    ipdata = r.json()
    return ipdata

def get_df(from_date, to_date, coin):
    """ Get historical price data between two dates. """
    date = to_date
    holder = []
    while date > from_date:
        data = get_data(date, coin)
        holder.append(pd.DataFrame(data['Data']))
        date = data['TimeFrom']
    # Join together all of the API queries in the list.    
    df = pd.concat(holder, axis = 0)                    
    # Remove data points from before from_date
    df = df[df['time']>from_date]                       
    # Convert to timestamp to readable date format
    df['time'] = pd.to_datetime(df['time'], unit='s')   
    # Make the DataFrame index the time
    df.set_index('time', inplace=True)                  
    # And sort it so its in time order 
    df.sort_index(ascending=False, inplace=True)        
    return df




top10CoinByMarketValue = ["BTC","XRP","ETH","BCH","USDT","LTC","CRO","EOS","DDAM","BNB"]

for i in top10CoinByMarketValue:
    #CHANGE HERE to change start or end time of data to retrieve
    df = get_df(1420074926, 1573351677, i)

    # CHANGE output file name
    df.to_csv("top10CoinHourlyData/" + i + '.csv')

