# 量化研究之成长股因子选股——模板化可定制(Quantitative research of growth stock factor)
Quantitative research of growth stock factor , the template can be customized or run in ricequant.com.



### 量化研究之成长股因子选股——模板化可定制

**[文章已发表在个人博客，欢迎点击这里访问](http://captxiong.pythonanywhere.com/detail-2)**

### 序

下面是博主之前在米匡量化平台做的一个因子研究，本来是自己写着玩玩，想来可能会有程序员朋友对此感兴趣的，就拿来分享一下。

平台有策略、研究两大块，策略部分分享一个博主的策略，现已上英雄榜可以[订阅](https://www.ricequant.com/scrafts/4109827)了。写这篇博客的时候打分榜第三名，让我嘚瑟一下。

由于平台经常更新，论坛的许多教程代码跑不通，博主还是以官方API文档为准，做了以下的选股模板。

亲测可以直接粘贴使用。选股板块、成长因子、时间均可自由发挥。

### 使用环境

米匡平台-研究板块

### 成长股因子选股

下面内容直接从研究板块导出md文件来的，排版较烂，结合注释理解吧，保留了部分结果显示。

此处写一个成长股因子打分选股部分,考虑TMT、医疗器械板块

- C34	通用设备制造业
- C35	专用设备制造业
- C36	汽车制造业
  C37	铁路、船舶、航空航天和其它运输设备制造业
- C38	电气机械及器材制造业
- C39	计算机、通信和其他电子设备制造业
- I63	电信、广播电视和卫星传输服务
- I64	互联网和相关服务
- I65	软件和信息技术服务业
- ~~J66	货币金融服务~~
- ~~J67	资本市场服务~~（由于选出的股票为银行类，这里未考虑J66/67，若是互联网金融方向可以考虑加入）

1.研发费用 
2.市值大小
3.~~波动率~~（去掉，波动率分析在博主另一篇研究中）
4.利润率
5.pe
6.季度净利润同比增长率（Gr_Q_Earning）（单季度营业利润同比增长率（Gr_Q_OpEarning）或单季度营业收入同比增长率（Gr_Q_Sale））（未实现）





```python
import talib
import pandas as pd
import numpy as np
import time
import math
import itertools
import matplotlib.pyplot as plt


```

```python
stock_all=[]
industry_sector=['C34','C35','C36','C37','C38','C39','I63','I64','I65']
for i in industry_sector:
    stock=industry(i)
    for u in stock:
        stock_all.append(u)

```

```python
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
```



```python
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

```

```python
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
    
```

```python
change_score(df_npr)
change_score(df_rnd)

df_pe['score_pe'] = range(len(df_pe),0,-1) #增加一列score
```

```python
#合并4个因子打分表到df_score
df_score=df_pe.join(df_npr)
df_score=df_score.join(df_rnd)

df_score['sum_score']=df_score['score_pe']+df_score['net_profit_to_revenue_score']+df_score['r_n_d_score']
df_score=df_score.sort_values(by='sum_score',ascending=False)
print(df_score)
```

```python
            pe_ratio  score_pe net_profit_to_revenue  \
002624.XSHE  20.2827        74               23.8204   
600741.XSHG  10.6567        93                6.5587   
000581.XSHE   9.0107        94               30.8232   
000425.XSHE  13.9095        90                 7.338   
600066.XSHG  13.6614        92                6.4961   
002195.XSHE     15.6        83               37.2389   
002236.XSHE  19.4177        75                7.0245   
000100.XSHE   13.833        91                3.3931   
002558.XSHE  38.3668        36               42.5748   
601877.XSHG  15.4906        84                9.5351   
000157.XSHE   14.632        87               10.8845   
600487.XSHG  15.2499        85                6.5195   
000418.XSHE  18.6541        76                9.3535   
600271.XSHG   23.386        71               12.6534   
600637.XSHG  18.2015        78               23.0387   
600570.XSHG  52.0446        18               65.6754   
002202.XSHE  14.7916        86                4.8468   
002555.XSHE  27.6106        62                14.951   
600528.XSHG  17.0272        80                7.6473   
600699.XSHG  16.1644        82                3.2768   
300296.XSHE  17.5456        79               15.2299   
000413.XSHE  16.3028        81               11.8094   
601869.XSHG  21.3844        73               15.4048   
600522.XSHG  14.1968        89                4.7687   
300003.XSHE  31.6784        48                30.803   
603160.XSHG  50.5612        19               33.8194   
600703.XSHG  21.4514        72                35.925   
000938.XSHE   31.048        53                5.0535   
300136.XSHE  25.6494        67               22.5093   
002008.XSHE  27.5432        63                7.4863   
...              ...       ...                   ...   
300773.XSHE  40.0761        33               12.4464   
300383.XSHE  36.9025        41               11.5507   
002353.XSHE  31.5145        52               11.4972   
002916.XSHE  43.4549        29                8.6252   
603515.XSHG  28.3965        60                5.1726   
000977.XSHE  47.2224        23                0.8898   
300529.XSHE  58.1142        15               43.8276   
002384.XSHE  33.4564        45                4.4626   
300308.XSHE  46.5002        26                11.363   
002129.XSHE  40.7193        32                6.1235   
300253.XSHE  70.7282        10               20.7637   
300766.XSHE  93.7558         1               42.8886   
002465.XSHE  49.2613        20                3.1105   
002153.XSHE   70.811         9               10.7012   
002602.XSHE  54.0131        17                9.0277   
002013.XSHE   31.624        49                2.4935   
603986.XSHG  66.5266        13                8.6706   
600320.XSHG  47.1206        24                1.4574   
601179.XSHG  42.8337        30                3.0229   
300024.XSHE  57.3201        16               10.6734   
002049.XSHE  68.6453        12                 9.988   
600150.XSHG   76.378         5                0.1429   
603019.XSHG  79.4685         3                  2.32   
600760.XSHG  44.6061        27                3.9009   
600959.XSHG  43.5013        28                 4.821   
600118.XSHG  64.5165        14                5.3741   
600893.XSHG  48.5943        21                 0.287   
600038.XSHG  48.3561        22                3.1286   
000768.XSHE  77.2604         4                0.5511   
600733.XSHG  82.0031         2                0.9936   

             net_profit_to_revenue_score        r_n_d  r_n_d_score  sum_score  
002624.XSHE                           82  4.56704e+08           88        244  
600741.XSHG                           35  1.28332e+09           94        222  
000581.XSHE                           85    9.317e+07           41        220  
000425.XSHE                           39  4.52528e+08           87        216  
600066.XSHG                           33   4.1695e+08           84        209  
002195.XSHE                           89  7.21105e+07           32        204  
002236.XSHE                           38  5.41327e+08           90        203  
000100.XSHE                           18  1.16205e+09           93        202  
002558.XSHE                           90  1.91154e+08           72        198  
601877.XSHG                           51  1.53096e+08           61        196  
000157.XSHE                           56  1.15699e+08           52        195  
600487.XSHG                           34  2.25941e+08           76        195  
000418.XSHE                           49  1.82898e+08           70        195  
600271.XSHG                           64  1.41382e+08           58        193  
600637.XSHG                           81  7.24097e+07           33        192  
600570.XSHG                           94   3.1214e+08           80        192  
002202.XSHE                           27  2.46322e+08           78        191  
002555.XSHE                           69  1.46393e+08           59        190  
600528.XSHG                           42  1.68004e+08           67        189  
600699.XSHG                           16  5.27403e+08           89        187  
300296.XSHE                           70  8.18656e+07           36        185  
000413.XSHE                           61  9.67752e+07           42        184  
601869.XSHG                           72  8.39481e+07           39        184  
600522.XSHG                           25   1.6476e+08           66        180  
300003.XSHE                           84  1.08688e+08           47        179  
603160.XSHG                           86  2.08864e+08           73        178  
600703.XSHG                           88  3.41314e+07           14        174  
000938.XSHE                           28  9.02578e+08           92        173  
300136.XSHE                           79  6.13005e+07           26        172  
002008.XSHE                           41   1.7195e+08           68        172  
...                                  ...          ...          ...        ...  
300773.XSHE                           63  6.34803e+07           27        123  
300383.XSHE                           60  4.95481e+07           21        122  
002353.XSHE                           59  2.93545e+07           11        122  
002916.XSHE                           44  1.05463e+08           46        119  
603515.XSHG                           29  6.57662e+07           29        118  
000977.XSHE                            4  4.31916e+08           85        112  
300529.XSHE                           92  1.33319e+07            5        112  
002384.XSHE                           23  8.19112e+07           37        105  
300308.XSHE                           57  4.94327e+07           20        103  
002129.XSHE                           32  8.34382e+07           38        102  
300253.XSHE                           76  3.89526e+07           16        102  
300766.XSHE                           91  2.34471e+07            9        101  
002465.XSHE                           14  1.53747e+08           62         96  
002153.XSHE                           55  7.05788e+07           31         95  
002602.XSHE                           46  6.67843e+07           30         93  
002013.XSHE                            8  8.04932e+07           34         91  
603986.XSHG                           45  6.40823e+07           28         86  
600320.XSHG                            6   1.2165e+08           53         83  
601179.XSHG                           13  8.09212e+07           35         78  
300024.XSHE                           54  1.08595e+07            4         74  
002049.XSHE                           53  1.00663e+07            3         68  
600150.XSHG                            1  1.48375e+08           60         66  
603019.XSHG                            7   1.1154e+08           50         60  
600760.XSHG                           20    2.841e+07           10         57  
600959.XSHG                           26  3.68412e+06            2         56  
600118.XSHG                           30  2.13345e+07            7         51  
600893.XSHG                            2  5.24764e+07           23         46  
600038.XSHG                           15  1.80412e+07            6         43  
000768.XSHE                            3  3.34097e+07           13         20  
600733.XSHG                            5  3.59638e+06            1          8  

[94 rows x 7 columns]
```



```python
#选择前5支股票
stocks=df_score.index[0:5].values
#选择排名倒数5支股票，建立对照组
stocks_test=df_score.index[-6:-1].values
print(stocks)
print(stocks_test)
```

```python
['002624.XSHE' '600741.XSHG' '000581.XSHE' '000425.XSHE' '600066.XSHG']
['600959.XSHG' '600118.XSHG' '600893.XSHG' '600038.XSHG' '000768.XSHE']
```



```python
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
```

```python
[-0.02688372 -0.01096118 -0.00875974 -0.01963428]
```

![](https://img-blog.csdnimg.cn/20190801113242820.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0NhcHRfWGlvbmc=,size_16,color_FFFFFF,t_70)



```python
#可以看出基本面打分组收益率明显较高，由于是普跌的行情，应该说整体抗跌水平更优吧。
```

