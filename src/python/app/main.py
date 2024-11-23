from branca.colormap import linear
import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

from data import read_and_process_data


def generate_map(district: gpd.GeoDataFrame, stop: gpd.GeoDataFrame, route: gpd.GeoDataFrame) -> folium.Map:
    m = folium.Map(location=(34.178293, 131.474129), zoom_start=15)
    score_cm = linear.viridis.scale(0, 10)
    folium.GeoJson(
        district,
        style_function=lambda x: {
            "fillColor": score_cm(x["properties"]["score"]),
            "color": "black",
            "weight": 1,
            "dashArray": "5, 5",
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["S_NAME", "name", "type", "distance", "hindo", "score"]),
    ).add_to(m)
    popup=folium.GeoJsonPopup(fields=["NAME", "HINDO"])
    folium.GeoJson(
        stop,
        popup=popup,
        marker=folium.Marker(icon=folium.Icon(icon='star')),
        style_function=lambda x: {
            "markerColor": "red"
        },
    ).add_to(m)
    folium.GeoJson(
        route,
        style_function=lambda x: {
            "color": "black",
            "weight": 5,
        },
    ).add_to(m)
    score_cm.caption = "Score color scale"
    score_cm.add_to(m)
    folium.LayerControl().add_to(m)
    return m


def main():
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

    district, stop, route = read_and_process_data()
    map = generate_map(district, stop, route)
    st_folium(map, use_container_width=True, height=720, returned_objects=[])

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
