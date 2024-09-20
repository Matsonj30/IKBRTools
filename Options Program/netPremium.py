from ibapi.client import EClient
from ibapi.common import BarData
from ibapi.common import TickerId
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.contract import Option
from ibapi.ticktype import TickTypeEnum
import threading
import time
import pandas as pd
import matplotlib as mpl


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)



class IBConnection(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, wrapper=self)
        self.data = {}
        self.data_ready = False
        self.next_order_id = None
    #IBConnect.connect would have connected, but it will now call this function instead
    #This funcion will also make the connection, but will additionally create a thread to help with overlapping requests 
    def connect(self, host, port, clientId):
        super().connect(host, port, clientId)
        thread = threading.Thread(target=self.run)
        thread.start()
        time.sleep(1)






def getSubsciptionData(IBConnect, ticker):
    #If you have market data, use this as opposed to the while loop below
    IBConnect.requestData(ticker, "1 D", "1 Min")
    while not(IBConnect.data_ready):
        time.sleep(1)
    df  = pd.DataFrame(IBConnect.data)
    print(df)


def main():
    IBConnect = IBConnection()
    IBConnect.connect("127.0.0.1", 7497, 0)
    #Use this line if you have not paid for a real time subscription
    IBConnect.reqMarketDataType(1)


    getSubsciptionData(IBConnect, "SPY")

if __name__ == "__main__":
    main()