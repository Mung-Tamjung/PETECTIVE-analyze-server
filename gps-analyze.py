# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:34:17 2024

@author: pjh10
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
import webbrowser

#해당 사용자의 최근 7일 간의 gps 기록 모두 불러오기('lat','lon')
#data=
data=[(37.6528, 127.0163), (37.6528, 127.0164), (37.6528, 127.0165), (37.6528, 127.0165)]

df = pd.DataFrame(data) #(칼럼:'lat', 'lon')
df.columns = ['lat', 'lon']
grouped_df = df.groupby(['lat','lon']).size().sort_values(ascending=False).to_frame('value_count').reset_index() #[:n] ->상위 n개 순위만 표시하고 샆은 경우엔 인덱스 처리

#산점도
plt.scatter(grouped_df.lat, grouped_df.lon, s=grouped_df.value_count*10)
plt.show()

#folium 지도
gps_map=folium.Map(location=[37.6528, 127.0163], zoom_Start=12) #지도 초기 로딩위치
for p in grouped_df.index:
    lat = grouped_df.loc[p, 'lat']
    lon = grouped_df.loc[p, 'lon']
    r=float(grouped_df.loc[p, 'value_count']) #radius값 int일 경우 오류 발생 -> float으로 바꿔주기
    folium.CircleMarker([lat, lon],
                        radius=r,
                        popup="("+str(grouped_df.loc[p, 'lat'])+","+str(grouped_df.loc[p, 'lon'])+")",
                        fill=True).add_to(gps_map)
    
gps_map.save("gps_map.html")
webbrowser.open("gps_map.html")

print(grouped_df)