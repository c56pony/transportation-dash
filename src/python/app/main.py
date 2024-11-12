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
    bus_stop = gpd.read_file("data/06_交通/C0604_バスの状況/GIS/C06041_H22_バス停の状況_OP.shp", encoding="shift-jis")
    bus_route = gpd.read_file("data/06_交通/C0604_バスの状況/GIS/C06042_H22_バス路線の状況_OP.shp", encoding="shift-jis")

    buffer_m = 10
    bs_bufferd = bus_stop.to_crs(epsg=3098).buffer(buffer_m)
    br_geometry = bus_route.to_crs(epsg=3098).geometry

    bs_hindo = []
    for bs in bs_bufferd:
        is_intersected = br_geometry.intersects(bs)
        bs_hindo.append(bus_route[is_intersected]["B_HINDO"].max())
    bus_stop["hindo"] = bs_hindo

    district = gpd.read_file("data/B002005212020DDSWC35203/r2kb35203.shp")
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
    st_folium(m, use_container_width=True, height=720, returned_objects=[])

if __name__ == "__main__":
    main()
