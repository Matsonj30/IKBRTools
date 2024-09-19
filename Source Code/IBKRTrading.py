from ibapi.client import EClient
from ibapi.common import BarData
from ibapi.common import TickerId
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import pandas as pd
from techAnalysis import TechnicalAnalysis
from orderManager import OrderManager

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
    
    def nextValidId(self, orderID: TickerId):
        super().nextValidId(orderID)
        self.next_order_id = orderID
        return self.next_order_id


    #called by reqHistoricalData for each available candle, we can then choose what data we want to grab, then put 
    #it inside of an array
    def historicalData(self, reqID, bar):
        if reqID not in self.data:
            self.data[reqID] = []
        
        self.data[reqID].append({
            "date": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        })


    def historicalDataEnd(self, reqId, start, end):
        self.data_ready = True

    def requestData(self, symbol, duration, barSize, uniqueReqId):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        #this will call historicalData for each candle that is available within these parameters
        self.reqHistoricalData(
            reqId = uniqueReqId, #keep this as 1 if you have a market subscription
            contract = contract,
            endDateTime= "", #Empty string recievbes the most recent data
            durationStr=duration,
            barSizeSetting=barSize,
            whatToShow="TRADES",
            useRTH = 0,
            formatDate= 1,
            keepUpToDate=True,#Update as we go by tick
            chartOptions=[] #no extra options
            
        )
    def newCandle(self, newBar):
        print(f"New Data Recieved. Latest bar: {newBar}")
        ta = TechnicalAnalysis()
        om = OrderManager(self)


        if(ta.hammerDetect(newBar)):
            print("Hammer Detected, Placing Order")

            buyContract = om.create_contract("SPY")
            order = om.create_bracket_order("BUY", 1, newBar["close"], newBar["close"] + 0.4, newBar["close"] - 0.4)

            for specificOrder in order:
                om.place_order(buyContract, specificOrder)



    # This is for when you have a market subscription 
    
    # def historicalDataUpdate(self, reqId, bar):
    #     self.data[reqId].append({
    #     "date": bar.date,
    #     "open": bar.open,
    #     "high": bar.high,
    #     "low": bar.low,
    #     "close": bar.close,
    #     "volume": bar.volume
    # })
    #     try:
    #         if(self.data[1][-1]["date"] != self.data[1][-2]["date"]):
    #             self.newCandle(self.data[1][-2])
    #     except Exception as e:
    #         print("Not enough candles in the dataset to compare")
        


def main():
    IBConnect = IBConnection()
    IBConnect.connect("127.0.0.1", 7497, 0)
    #Use this line if you have not paid for a real time subscription
    IBConnect.reqMarketDataType(3)

    #If you have market data, use this as opposed to the while loop below
    # IBConnect.requestData("SPY", "1 D", "1 Min")
    # while not(IBConnect.data_ready):
    #     time.sleep(1)
    # df  = pd.DataFrame(IBConnect.data)
    # print(df)

    #Use this without a market subscription
    uniqueReqId = 1
    while True:
        IBConnect.requestData("SPY", "1 D", "1 Min", uniqueReqId)
        while not(IBConnect.data_ready):
            time.sleep(1)
        
        IBConnect.newCandle(IBConnect.data[uniqueReqId][-1])
        df  = pd.DataFrame(IBConnect.data)
        #print(df)
        IBConnect.data = {}
        IBConnect.data_ready = False
        uniqueReqId += 1
        time.sleep(60)


if __name__ == "__main__":
    main()