import talib
import pandas as pd
import numpy as np
import time
import math
import itertools
import matplotlib.pyplot as plt

stock_all=[]
industry_sector=['C34','C35','C36','C37','C38','C39','I63','I64','I65']
for i in industry_sector:
    stock=industry(i)
    for u in stock:
        stock_all.append(u)

fundamental_df = get_fundamentals(
        query(fundamentals.eod_derivative_indicator.market_cap,
              fundamentals.eod_derivative_indicator.pe_ratio,
              fundamentals.income_statement.r_n_d,
              fundamentals.financial_indicator.net_profit_to_revenue
             ).filter(
              fundamentals.income_statement.stockcode.in_(stock_all)
            ).filter(
              fundamentals.eod_derivative_indicator.pe_ratio<100
            ).filter(
              fundamentals.financial_indicator.net_profit_to_revenue>0
            ).filter(
            fundamentals.eod_derivative_indicator.pe_ratio>0
            ). filter(
              fundamentals.eod_derivative_indicator.market_cap>20000000000
            ).filter(
              fundamentals.eod_derivative_indicator.market_cap<80000000000
            ).order_by(
            fundamentals.eod_derivative_indicator.pe_ratio
            ),entry_date='2019-4-30',interval='1q'
       ,expect_df=False)
fundamental_df.dropna()

#npr净利润/营业总收入,rnd研发费用,pe动态市盈率
df_pe = fundamental_df['pe_ratio']
df_rnd = fundamental_df['r_n_d']
df_npr = fundamental_df['net_profit_to_revenue']

df_pe=df_pe.T
df_npr=df_npr.T
df_rnd=df_rnd.T
#修改列名字
df_pe.columns=['pe_ratio']
df_rnd.columns=['r_n_d']
df_npr.columns=['net_profit_to_revenue']

#将因子筛选的股票排序打分
def change_score(df):
#新建df_newdyr，排序，打分
    df_newdyr=df.sort_values(by=df.columns[0],axis = 0,ascending = True)
    df_newdyr['new_score']=range(1,len(df_newdyr)+1)
    score_dyr=[]#新建股息率分数列，按原股票顺序排好，等会插入到df_dyr中
    #遍历df_newdyr，获取每只股票的股息率分数
    for i in range(0,len(df_newdyr)):
        score_dyr.append(df_newdyr.loc[df.index[i]][1])
        score_dyr=score_dyr
    col_name=df.columns[0]+'_score'
    df[col_name]=score_dyr 
    
change_score(df_npr)
change_score(df_rnd)
df_pe['score_pe'] = range(len(df_pe),0,-1) #增加一列score

#合并4个因子打分表到df_score
df_score=df_pe.join(df_npr)
df_score=df_score.join(df_rnd)

df_score['sum_score']=df_score['score_pe']+df_score['net_profit_to_revenue_score']+df_score['r_n_d_score']
df_score=df_score.sort_values(by='sum_score',ascending=False)
print(df_score)

#选择前5支股票
stocks=df_score.index[0:5].values
#选择排名倒数5支股票，建立对照组
stocks_test=df_score.index[-6:-1].values
print(stocks)
print(stocks_test)

#假设平均持有以上5支股票三个月，对比基准为上证300指数、创业板指数
#获取股票及指数每日收盘价，计算期间收益率。

stocks_bench=np.array(['000300.XSHG','399006.XSHE'])
bench_close=get_price(stocks_bench, start_date='2019-04-30', end_date='2019-07-30', frequency='1d', fields='close')
stocks_close=get_price(stocks, start_date='2019-04-30', end_date='2019-07-30', frequency='1d', fields='close')
test_close=get_price(stocks_test, start_date='2019-04-30', end_date='2019-07-30', frequency='1d', fields='close')
#定义求收益率函数
def a_return(close):
    return (close.iloc[-1,:]-close.iloc[0,:])/close.iloc[0,:]

stocks_return=a_return(stocks_close)
bench_return=a_return(bench_close)
test_return=a_return(test_close)
#计算平均收益率
stocks_avg=stocks_return.sum()*0.2
test_avg=test_return.sum()*0.2

#绘制柱状图对比
data=np.append(bench_return,[stocks_avg,test_avg])
print(data)
data_bar = pd.Series(data, index=list(['沪深300指数','创业板指数','打分前5名','对照组test']))
data_bar.plot(kind='bar', figsize=(15, 6), fontsize=12)
plt.title('2019-4-30至2019-7-30收益率情况')

#可以看出基本面打分组收益率明显较高，由于是普跌的行情，应该说整体抗跌水平更优吧。