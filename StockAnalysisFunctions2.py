import pandas as pd
import datetime as dt
import numpy as np
import yfinance as yf

import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SFA:
    TICKER, SOURCE, VAR, DESC, DATA = 0,1,2,3,4  # Constants for Dictionary List entry
    
    def __init__(self):
        pass
    
    def get_ticker_description(self, ticker):
        return yf.Ticker(ticker).info['longName']

    def get_stock_data(self, ticker, start_date, end_date,
                       return_description = False):
        df = yf.download(ticker, start = start_date,
                         end = end_date)
        if return_description:
            desc = yf.Ticker(ticker).info['longName']
            return df,desc
        else:
            return df

    def add_moving_avgs(self,df_):
        df_['200d SMA'] = df_['Close'].rolling(window=200).mean()
        df_['50d SMA'] = df_['Close'].rolling(window=50).mean()
        df_['5d SMA'] = df_['Close'].rolling(window=5,center=True).mean()
        return df_

    def add_daily_return(self,df_):
        df_['daily_return'] = (df_['Close']/df_['Close'].shift(1)) - 1.0
        return df_

    def add_cumulative_return(self,df_):
        df_ = self.add_daily_return(df_)
        df_['cumulative_return'] = (1.0 + df_['daily_return']).cumprod()
        return df_

    def add_bollinger_bands(self,df_):
        df_['bb_mid_band'] = df_['Close'].rolling(window=20).mean()
        df_['rolling_std'] = df_['Close'].rolling(window=20).std()
        df_['bb_upper'] = df_['bb_mid_band'] + 2.0 * df_['rolling_std']
        df_['bb_lower'] = df_['bb_mid_band'] - 2.0 * df_['rolling_std']
        df_['bb_upper_no_man'] = df_['bb_mid_band'] + 1.0 * df_['rolling_std']
        df_['bb_lower_no_man'] = df_['bb_mid_band'] - 1.0 * df_['rolling_std']
        return df_

    def add_ichimoku(self,df_):
        # Conversion
        hi_val = df_['High'].rolling(window=9).max()
        low_val = df_['Low'].rolling(window=9).min()
        df_['conversion_line'] = (hi_val + low_val) / 2

        # Baseline
        hi_val2 = df_['High'].rolling(window=26).max()
        low_val2 = df_['Low'].rolling(window=26).min()
        df_['baseline'] = (hi_val2 + low_val2) / 2

        # Spans
        df_['span_a'] = ((df_['conversion_line'] + df_['baseline']) / 2).shift(26)
        hi_val3 = df_['High'].rolling(window=52).max()
        low_val3 = df_['Low'].rolling(window=52).min()
        df_['span_b'] = ((hi_val3 + low_val3) / 2).shift(26)
        df_['lagging_line'] = df_['Close'].shift(-26)
        return df_
    
    def plot_with_ma(self, df_, title_):
        
        fig = go.Figure()

        candle = go.Candlestick(x=df_.index, open=df_['Open'],
        high=df_['High'], low=df_['Low'],
        close=df_['Close'], showlegend=True,
                                name="Candlestick")

        sma200= go.Scatter(x=df_.index, y=df_['200d SMA'], 
        line=dict(color='rgba(0, 150, 2255, 0.75)', 
        width=2), name="200d SMA")

        sma50 = go.Scatter(x=df_.index, y=df_['50d SMA'], 
        line=dict(color='rgba(128, 0, 128, 0.75)', 
        width=2,dash='dash'), name="50d SMA")

        sma5 = go.Scatter(x=df_.index, y=df_['5d SMA'], 
        line=dict(color='rgba(0, 0, 0, 1)', 
        width=1), name="5d SMA")

        fig.add_trace(sma200)
        fig.add_trace(sma50)
        fig.add_trace(sma5)
        fig.add_trace(candle)
        
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_yaxes(title="Price")

        fig.update_layout(title=title_ + " Moving Averages",
                          showlegend=True,
                          legend=dict(orientation = 'h',
                                      yanchor="top", y=-0.5,
                                      xanchor="center", x=0.5))
        # height=500, width=900, 
        return fig
    
    
    def plot_with_boll_bands(self, df_, title_):
        
        fig = go.Figure()

        candle = go.Candlestick(x=df_.index, open=df_['Open'],
        high=df_['High'], low=df_['Low'],
        close=df_['Close'], showlegend=True,
                                name="Candlestick")

        upper_line = go.Scatter(x=df_.index, y=df_['bb_upper'], 
        line=dict(color='rgba(100, 149, 237, 0.75)', 
        width=1), name="Upper Band")

        upper_line_no_man = go.Scatter(x=df_.index, y=df_['bb_upper_no_man'], 
        line=dict(color='rgba(100, 149, 237, 0.75)', 
        width=1,dash='dash'), name="Upper No Mans Zone")

        lower_line = go.Scatter(x=df_.index, y=df_['bb_lower'], 
        line=dict(color='rgba(255, 140, 0, 0.75)', 
        width=1), name="Lower Band")

        lower_line_no_man = go.Scatter(x=df_.index, y=df_['bb_lower_no_man'], 
        line=dict(color='rgba(255, 140, 0, 0.75)', 
        width=1,dash='dash'), name="Lower No Mans Zone")



        fig.add_trace(upper_line)
        fig.add_trace(upper_line_no_man)
        fig.add_trace(lower_line)
        fig.add_trace(lower_line_no_man)
        fig.add_trace(candle)
        
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_yaxes(title="Price")

        fig.update_layout(title=title_ + " Bollinger Bands",
                          showlegend=True,
                          legend=dict(orientation = 'h',
                                      yanchor="top", y=-0.5,
                                      xanchor="center", x=0.5))
        # height=500, width=900, 
        return fig
        
    # Used to generate the red and green fill for the Ichimoku cloud
    def get_fill_color(self, label):
        if label >= 1:
            return 'rgba(0,250,0,0.4)'
        else:
            return 'rgba(250,0,0,0.4)'

    def plot_ichimoku(self, df_,title_):

        candle = go.Candlestick(x=df_.index, open=df_['Open'],
        high=df_['High'], low=df_["Low"], close=df_['Close'],
        showlegend=True,name="Candlestick")

        df_1 = df_.copy()
        fig = go.Figure()
        df_['label'] = np.where(df_['span_a'] > df_['span_b'], 1, 0)
        df_['group'] = df_['label'].ne(df_['label'].shift()).cumsum()

        df_ = df_.groupby('group')

        df_s = []
        for name, data in df_:
            df_s.append(data)

        for df_ in df_s:
            fig.add_traces(go.Scatter(x=df_.index, y=df_.span_a,
            line=dict(color='rgba(0,0,0,0)'),showlegend=False))

            fig.add_traces(go.Scatter(x=df_.index, y=df_.span_b,
            line=dict(color='rgba(0,0,0,0)'),
            fill='tonexty',
            fillcolor=self.get_fill_color(df_['label'].iloc[0]),
            showlegend=False))

        baseline = go.Scatter(x=df_1.index, y=df_1['baseline'], 
        line=dict(color='black', width=1), name="Baseline")

        conversion_line = go.Scatter(x=df_1.index, y=df_1['conversion_line'], 
        line=dict(color='pink', width=2), name="Conversion Line")

        lagging_line = go.Scatter(x=df_1.index, y=df_1['lagging_line'], 
        line=dict(color='purple', width=1,dash='dot'), name="Lag Line")

        span_a = go.Scatter(x=df_1.index, y=df_1['span_a'], 
        line=dict(color='green', width=2, dash='dot'), name="Span A")

        span_b = go.Scatter(x=df_1.index, y=df_1['span_b'], 
        line=dict(color='red', width=1, dash='dot'), name="Span B")

        fig.add_trace(span_b)
        fig.add_trace(span_a)
        fig.add_trace(lagging_line)
        fig.add_trace(conversion_line)
        fig.add_trace(baseline)
        fig.add_trace(candle)
        
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_yaxes(title="Price")
        
        fig.update_layout(title=title_ + " Ichimoku",
                          showlegend=True,
                          legend=dict(orientation = 'h',
                                      yanchor="top", y=-0.4,
                                      xanchor="center", x=0.5))
        # height=500, width=900, 
        
        return fig