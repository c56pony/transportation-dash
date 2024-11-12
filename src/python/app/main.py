#!/usr/bin/env python
# coding: utf-8

import folium
from branca.colormap import linear
import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import numpy as np

import streamlit as st
from streamlit_folium import st_folium


def main():
    bus_stop = gpd.read_file("data/bus/C0604_バスの状況/GIS/C06041_H22_バス停の状況_OP.shp", encoding="shift-jis")
    bus_route = gpd.read_file("data/bus/C0604_バスの状況/GIS/C06042_H22_バス路線の状況_OP.shp", encoding="shift-jis")

    buffer_m = 10
    bs_bufferd = bus_stop.to_crs(epsg=3098).buffer(buffer_m)
    br_geometry = bus_route.to_crs(epsg=3098).geometry

    bs_hindo = []
    for bs in bs_bufferd:
        is_intersected = br_geometry.intersects(bs)
        bs_hindo.append(bus_route[is_intersected]["B_HINDO"].max())
    bus_stop["hindo"] = bs_hindo

    district = gpd.read_file("data/district/B002005212020DDSWC35203/r2kb35203.shp")
    district = district[district.KIHON1.astype(float) < 300]

    bs_point = bus_stop.to_crs(epsg=3098).geometry
    bs_point = np.array([(point.x, point.y) for point in bs_point])
    district_centroid = district.to_crs(epsg=3098).centroid
    district_centroid = np.array([(point.x, point.y) for point in district_centroid])
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(bs_point)
    distance, idx = nn.kneighbors(district_centroid)
    district["distance"] = distance
    district["bus_stop"] = bus_stop["B_NAME"][idx.flatten()].values
    district[["bus_stop", "distance"]].head(5)

    m = folium.Map(location=(34.178293, 131.474129), zoom_start=15)
    distance_cm = linear.YlGn_09.scale(0, 800) # 5km/h * 5min *2
    folium.GeoJson(
        district,
        style_function=lambda x: {
            "fillColor": distance_cm(x["properties"]["distance"]),
            "color": "black",
            "weight": 1,
            "dashArray": "5, 5",
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["S_NAME", "bus_stop", "distance"]),
    ).add_to(m)
    popup=folium.GeoJsonPopup(fields=["B_NAME", "hindo"])
    folium.GeoJson(
        bus_stop,
        popup=popup,
        marker=folium.Marker(icon=folium.Icon(icon='star')),
        style_function=lambda x: {
            "markerColor": "red"
        },
    ).add_to(m)
    hindo_cm = linear.YlGn_09.scale(0, 25)
    folium.GeoJson(
        bus_route,
        style_function=lambda x: {
            "color": hindo_cm(x["properties"]["B_HINDO"]),
            "weight": 5,
        },
        tooltip=folium.GeoJsonTooltip(fields=["B_ROSEN", "B_HINDO"]),
    ).add_to(m)

    st.set_page_config(
        page_title="山口市交通機関身近度マップ",
        page_icon="🚌",
        layout="wide"
    )
    st.title("山口市交通機関身近度マップ")
    st.markdown(
        """
        本サイトは、山口市の交通機関身近度を可視化したマップです。以下の機能を提供しています：

        - **地域別の交通機関身近度**：地域ごとに最寄りのバス停までの距離を表示します。
        - **バス停の利用頻度**：バス停ごとの利用頻度を表示します。
        - **バス路線の利用頻度**：バス路線ごとの利用頻度を表示します。

        交通機関身近度を確認することで、住宅選びや移動手段の検討に役立ててください。また、本サイトで使用しているデータの出典と加工内容についても記載していますので、ご参照ください。
        """
    )
    with st.container(height=750):
        st_folium(m, use_container_width=True, height=720, returned_objects=[])
    st.markdown(
            """
            ##### 出典

            本サイトで使用しているデータは、以下の出典から取得し、加工したものです：

            1. **山口県オープンデータカタログサイト**
               - ライセンス: [PDL1.0](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)
               - データ: [【山口県】都市計画基礎調査結果](https://yamaguchi-opendata.jp/ckan/dataset/toshikeikakukisotyousa)
               - 出典URL: [山口県オープンデータカタログサイト](https://yamaguchi-opendata.jp/)

            2. **政府統計の総合窓口（e-Stat）**
               - ライセンス: [利用規約](https://www.e-stat.go.jp/terms-of-use)
               - データ: [境界データ](https://www.e-stat.go.jp/gis/statmap-search?type=2)
               - 出典URL: [政府統計の総合窓口（e-Stat）](https://www.e-stat.go.jp/)

            ##### 加工内容

            本サイトで公開しているデータは、上記出典から取得したデータを元に加工したものです。具体的な加工内容は以下の通りです：

            - 都市計画基礎調査結果データを統合して、地域別の詳細な分析を行いました。
            - 境界データを使用して、地理情報システム（GIS）に適した形式に変換しました。

            これらのデータは、山口県オープンデータカタログサイトおよび政府統計の総合窓口（e-Stat）に帰属しています。
            """
    )

if __name__ == "__main__":
    main()
