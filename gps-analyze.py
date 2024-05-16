from flask import Flask
import pandas as pd
import matplotlib.pyplot as plt
import folium

app = Flask(__name__)

@app.route('/')
def hello_pybo():
    return 'Hello, Pybo!'


@app.route('/gps')  #/gps/<userid> - get_gps(userid)
def get_gps():
    # 해당 사용자의 최근 7일 간의 gps 기록 모두 불러오기('lat','lon')
    # data=
    data = [(37.6528, 127.0163), (37.6528, 127.0164), (37.6528, 127.0165), (37.6528, 127.0165), (37.6528, 127.0162),
            (37.6525, 127.0162)]

    # (칼럼:'lat', 'lon')
    # (lat, lon) count&sort
    df = pd.DataFrame(data)
    df.columns = ['lat', 'lon']
    grouped_df = df.groupby(['lat', 'lon']).size().sort_values(ascending=False).to_frame(
        'value_count').reset_index()  # [:n] ->상위 n개 순위만 표시하고 샆은 경우엔 인덱스 처리

    # 산점도
    plt.scatter(grouped_df.lat, grouped_df.lon, s=grouped_df.value_count * 10)
    plt.show()

    # folium 지도
    gps_map = folium.Map(location=[37.6528, 127.0163], zoom_Start=50)  # 지도 초기 로딩위치
    for p in grouped_df.index:
        lat = grouped_df.loc[p, 'lat']
        lon = grouped_df.loc[p, 'lon']
        r = float(grouped_df.loc[p, 'value_count'])
        folium.CircleMarker([lat, lon],
                            radius=r * 10,
                            popup="(" + str(grouped_df.loc[p, 'lat']) + "," + str(grouped_df.loc[p, 'lon']) + ")",
                            fill=True).add_to(gps_map)

    return gps_map.get_root().render()
