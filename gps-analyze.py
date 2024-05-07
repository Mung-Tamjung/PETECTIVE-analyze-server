# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:34:17 2024

@author: pjh10
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#해당 사용자의 최근 7일 간의 gps 기록 모두 불러오기('lat','lon')
#data=
data=[(37.6528, 127.0163), (37.6528, 127.0164), (37.6528, 127.0165), (37.6528, 127.0165)]

df = pd.DataFrame(data) #(칼럼:'lat', 'lon')
df.columns = ['lat', 'lon']
grouped_df = df.groupby(['lat','lon']).size().sort_values(ascending=False).to_frame('value_count').reset_index() #[:n] ->상위 n개 순위만 표시하고 샆은 경우엔 인덱스 처리
print(grouped_df)