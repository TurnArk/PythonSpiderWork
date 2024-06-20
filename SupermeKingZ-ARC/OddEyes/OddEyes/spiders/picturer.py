# -*- coding: GBK -*-
import chardet
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties

class ZARC:
    def draw(self,url_path = '../../../Data/dataHandle.csv',font_path='../../../Font/simsun.ttc'):
        with open(url_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
        with open(url_path, 'r', encoding=encoding) as file:
            df = pd.read_csv(file, header=0)
        df.columns = df.columns.str.strip()
        # print(df.columns)
        sns.set_style('whitegrid')
        plt.figure(figsize=(10, 6))
        line_plot = sns.lineplot(data=df, x='year', y='number', hue='classes', marker='o')
        for line in line_plot.lines:
            for x, y in zip(line.get_xdata(), line.get_ydata()):
                line_plot.text(x, y, f'{y:.0f}', color=line.get_color(), ha='right', va='bottom')
        font_type=FontProperties(font_path)
        line_plot.set_title('部分番剧类型五年来播放量变化图',fontproperties=font_type)
        line_plot.set_xlabel('年份/年',fontproperties=font_type)
        line_plot.set_ylabel('播放量/次',fontproperties=font_type)
        line_plot.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.show()

#ZARC().draw()