#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# K线图

# 导入第三方库
import tushare as ts
import matplotlib.finance as mpf
import matplotlib.pyplot as plt

from matplotlib.pylab import date2num
import datetime

from minnie.common import moracle

cursor = moracle.OralceCursor()

# 查询上证的历年数据
# 时间，开盘，收盘，最高，最低，交易量，代码
sql = """
    SELECT
  TO_DATE(STOCK_DATE, 'YYYY-MM-DD'),
  TO_NUMBER(OPEN_MARKET),
  TO_NUMBER(CLOSE_MARKET),
  TO_NUMBER(MAX_PRICE),
  TO_NUMBER(MIN_PRICE),
  TO_NUMBER(VOL),
  STOCK_CODE
FROM STOCK_NEW_VALUE_HISTORY
WHERE STOCK_CODE = '000001' 
"""
_date = cursor.fechall(sql)
mat_wdyx = []

for temp in _date:
    t1 = [date2num(temp[0])]
    t1 += list(temp[1:])
    mat_wdyx.append(t1)

fig, ax = plt.subplots(figsize=(15, 5))
fig.subplots_adjust(bottom=0.5)
mpf.candlestick_ochl(ax, mat_wdyx, width=0.6, colorup='g', colordown='r', alpha=1.0)
plt.grid(True)
# 设置日期刻度旋转的角度
plt.xticks(rotation=30)
plt.title('wanda yuanxian 17')
plt.xlabel('Date')
plt.ylabel('Price')
# x轴的刻度为日期
ax.xaxis_date()
# candlestick_ochl()函数的参数
# ax 绘图Axes的实例
# mat_wdyx 价格历史数据
# width    图像中红绿矩形的宽度,代表天数
# colorup  收盘价格大于开盘价格时的颜色
# colordown   低于开盘价格时矩形的颜色
# alpha      矩形的颜色的透明度

plt.show()
