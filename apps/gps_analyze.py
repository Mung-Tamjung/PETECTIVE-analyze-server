import pandas as pd
import matplotlib.pyplot as plt
import folium
from flask import Blueprint, jsonify
from database import engine
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

# app = Flask(__name__)
app_gps = Blueprint('app_gps', __name__)


@app_gps.route('/gps', methods=['GET'])
def home():
    conn = engine.raw_connection()
    sql = "select * from post_entity"
    result = pd.read_sql(sql, con = conn).values.tolist()
    data= {"data": result}
    return jsonify(data)#'gps_home'


@app_gps.route('/gps/<string:user_id>', methods=['GET'])  # /gps/<userid> - get_gps(userid)
def get_gps(user_id): #데이터 수가 너무 적은 경우 분석 불가 -> 에러처리
    # user_id로 DB에 사용자 검색(if문: 사용자 유무 판단)
    # 해당 사용자의 최근 7일 간의 gps 기록 모두 불러오기('lat','lon')
    date1 = datetime.now()#.strftime('%Y-%m-%d')
    date2 = date1 - timedelta(days=7)
    date1= date1.strftime('%Y-%m-%d')
    date2= date2.strftime('%Y-%m-%d')

    conn = engine.raw_connection()
    sql = f"select e.path from exercise_entity e where e.userid='{user_id}' and e.date <= '{date1}' and e.date >= '{date2}'"#where절: userid, 날짜(지난 7주일) 확인
    data = pd.read_sql(sql, con = conn) #.values.tolist()
    #print(data)

    # (칼럼:'lat', 'lon')
    # (lat, lon) count&sort
    df = pd.DataFrame(data)
    #print(df)

    lat_list = []
    lon_list = []
    for index, row in enumerate(df['path']):
        #print(type(row)) #str
        row = row[1:len(row)-1]
        row = row.replace('\"latitude\":','')
        row = row.replace('\"longitude\":','')
        #print(row) #str {37.6516133,127.0138233},{37.6516133,127.0138233},{37.6516133,127.0138233},{37.6516133,127.0138233},{37.6516133,127.0138233}
        row = row.replace('{', '')
        row = row.replace('}','')
        #print(row) #str 37.6516133,127.0138233,37.6516133,127.0138233,37.6516133,127.0138233,37.6516133,127.0138233,37.6516133,127.0138233
        row = row.split(',')
        for i in range(len(row)):
            if(i%2==0): lat_list.append(float(row[i]))
            else: lon_list.append(float(row[i]))

    #print(lat_list)
    #print(lon_list)

    gps_df = pd.DataFrame({"lat": lat_list, "lon": lon_list})
    #print(gps_df)
    #df.columns = ['lat','lon']
    # #gps_df.columns=['lat','lon']
    # gps 빈도 측정
    grouped_df = gps_df.groupby(['lat', 'lon']).size().sort_values(ascending=False).to_frame(
        'value_count').reset_index()  # [:n] ->상위 n개 순위만 표시하고 샆은 경우엔 인덱스 처리

    gps_map = folium.Map(location=[lat_list[0], lon_list[0]], zoom_Start=50)  # 지도 초기 로딩위치
    lost_location = [[37.6528, 127.0161]] #실종 위치 임의 지정

    # 데이터가 충분한 경우 클러스터 군집화 수행
    try:
        # 해당 사용자의 반려동물 산책 데이터 분석
        from sklearn.metrics import silhouette_score, silhouette_samples
        # 1. 산책 경로 군집화(클러스터링)
        # 1.1 최적 클러스터 찾기(엘보우)
        X_features = grouped_df[['lat', 'lon']].values
    #    distortions = []
    #    for i in range(1, 5):
    #        kmeans_i = KMeans(n_clusters=i, random_state=0)
    #        kmeans_i.fit(X_features)
    #        distortions.append(kmeans_i.inertia_)

    #    plt.plot(range(1, 5), distortions, marker='o')
    #    plt.xlabel('Number of clusters')
    #    plt.ylabel('Distortion')
    #    plt.show()

        n_cluster = 3
        kmeans = KMeans(n_clusters=n_cluster, random_state=0)
        Y_labels = kmeans.fit_predict(X_features)
        grouped_df['cluster_label'] = Y_labels
        print(X_features)

        # 1.2 클러스터 분포 차트 확인
    #    from matplotlib import cm
    #    for i in range(n_cluster):
    #        c_color = cm.jet(float(i) / n_cluster)
    #        plt.scatter(X_features[Y_labels == i, 0], X_features[Y_labels == i, 1], marker='o', color=c_color, s=30,
    #                    label='cluster' + str(i))
    #        plt.scatter(kmeans.cluster_centers_[i, 0], kmeans.cluster_centers_[i, 1], marker='^', color=c_color,
    #                    edgecolor='w', s=20)
    #    plt.legend()
    #    plt.grid()
    #    plt.tight_layout()
    #    plt.show()

        # 2. 동물의 실종된 위치가 어느 군집에 해당하는지 파악
        #lost_location = [[37.6528, 127.0161]] #실종 위치 임의 지정
        lost_predict = kmeans.predict(lost_location)
        #print(lost_predict)
        # 3. 해당 군집 경로 기반으로 현재 동물 위치 예측

        # 산점도
        # plt.scatter(grouped_df.lat, grouped_df.lon, s=grouped_df.value_count * 10)
        # plt.show()

        # folium 지도
        #gps_map = folium.Map(location=[lat_list[0], lon_list[0]], zoom_Start=50)  # 지도 초기 로딩위치

        for p in grouped_df.index:
            lat = grouped_df.loc[p, 'lat']
            lon = grouped_df.loc[p, 'lon']
            r = float(grouped_df.loc[p, 'value_count'])
            c = grouped_df.loc[p, 'cluster_label']

            color = 'grey'
            if (c == lost_predict[0]):
                color = 'green'

            folium.CircleMarker([lat, lon],
                                radius=r * 10,
                                color=color,
                                popup="(" + str(grouped_df.loc[p, 'lat']) + "," + str(
                                    grouped_df.loc[p, 'lon']) + ")" + ": cluster" + str(c),
                                fill=True).add_to(gps_map)
            # 실종 위치 마커
            folium.Marker([lost_location[0][0], lost_location[0][1]],
                          radius=10,
                          color='red',
                          popup="(" + str(grouped_df.loc[p, 'lat']) + "," + str(
                              grouped_df.loc[p, 'lon']) + ")" + ": cluster" + str(lost_predict[0]),
                          fill=True).add_to(gps_map)

    # 데이터가 충분하지 않은 경우 분석 과정 중 에러 발생 -> 군집화 수행X
    except:
        for p in grouped_df.index:
            lat = grouped_df.loc[p, 'lat']
            lon = grouped_df.loc[p, 'lon']
            r = float(grouped_df.loc[p, 'value_count'])

            folium.CircleMarker([lat, lon],
                                radius=r * 10,
                                color='grey',
                                popup="(" + str(grouped_df.loc[p, 'lat']) + "," + str(
                                    grouped_df.loc[p, 'lon']) + ")" ,
                                fill=True).add_to(gps_map)


        # 실종 위치 마커
        folium.Marker([lost_location[0][0], lost_location[0][1]],
                      radius=10,
                      color='red',
                      popup="(" + str(grouped_df.loc[p, 'lat']) + "," + str(
                          grouped_df.loc[p, 'lon']) + ")",
                      fill=True).add_to(gps_map)

    return gps_map.get_root().render()
