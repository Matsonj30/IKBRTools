class TechnicalAnalysis:
    def __init__(self):
        pass

    def hammerDetect(self, bar):
        bodySize = abs(bar['open'] - bar['close'])

         #calculate lower wick
        if bar['open'] > bar['close']:
            #red
            lower_wick = abs(bar['close'] - bar['low'])
        else:
            #green
            lower_wick = abs(bar['open'] - bar['low'])

        #calculate top wick
        if bar['open'] > bar['close']:
            #red
            upper_wick = abs(bar['high'] - bar['open'])
        else:
            #green candle
            upper_wick = abs(bar['high'] - bar['close'])
        
        isHammer = lower_wick >= bodySize and upper_wick < bodySize * 0.25

        isInvertedHammer = upper_wick >= bodySize and lower_wick < bodySize * 0.25
        
        return isHammer or isInvertedHammer
