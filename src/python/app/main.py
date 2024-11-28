import cmcrameri.cm as cmc
import folium
import geopandas as gpd
import streamlit as st
from branca.colormap import linear, LinearColormap
from streamlit_folium import st_folium

from data import read_and_process_data, filter_by_cluster


def generate_map(district: gpd.GeoDataFrame, stop: gpd.GeoDataFrame, route: gpd.GeoDataFrame) -> folium.Map:
    m = folium.Map(location=(34.178293, 131.474129), zoom_start=15)
    score_cm = [tuple(rgb) for rgb in cmc.batlow.colors.tolist()]
    score_cm = LinearColormap(score_cm, vmin=0, vmax=10)
    score_cm.caption = "アクセス度"
#   clusters = district["cluster"].unique().tolist()
#   cluster_dict = {c: i for i, c in enumerate(clusters)}
#   score_cm = linear.Set1_09.to_step(len(clusters)).scale(-0.5, len(clusters) + 0.5)
    folium.GeoJson(
        district,
        name="アクセス度",
        style_function=lambda x: {
            "fillColor": score_cm(x["properties"]["score"]),
#           "fillColor": score_cm(cluster_dict[x["properties"]["cluster"]]),
            "color": "black",
            "weight": 1,
            "dashArray": "5, 5",
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["S_NAME", "name", "type", "distance", "hindo", "score"]),
    ).add_to(m)

    icon_colors = {"bus": "darkblue", "train": "darkred"}
    popup = folium.GeoJsonPopup(fields=["NAME", "HINDO"])
    folium.GeoJson(
        stop,
        name="駅・バス停",
        popup=popup,
        marker=folium.Marker(icon=folium.Icon(prefix='fa')),
        style_function=lambda x: {
            "icon": x["properties"]["TYPE"],
            "markerColor": icon_colors[x["properties"]["TYPE"]],
        },
    ).add_to(m)

    route_colors = {
        "blue": "#43A9E2",
        "green": "#76B000",
        "red": "#D14020",
        "orange": "#F19800",
        "darkblue": "#1266A8",
        "darkgreen": "#738300",
        "darkred": "#983232",
    }
    folium.GeoJson(
        route,
        name="路線",
        style_function=lambda x: {
            "color": route_colors[icon_colors[x["properties"]["TYPE"]]],
            "weight": 3,
        },
    ).add_to(m)
    score_cm.add_to(m)
    folium.LayerControl().add_to(m)
    return m


def main():
    st.set_page_config(
        page_title="山口市交通機関アクセス度マップ",
        page_icon="🚌",
        layout="wide"
    )
    st.title("山口市交通機関アクセス度マップ")
    st.markdown(
        """
        本サイトは、山口市の交通機関アクセス度を可視化したマップです。以下の機能を提供しています：

        - **地域別の交通機関アクセス度**：地域ごとに最寄りのバス停までの距離を表示します。
        - **バス停の利用頻度**：バス停ごとの利用頻度を表示します。
        - **バス路線の利用頻度**：バス路線ごとの利用頻度を表示します。

        交通機関アクセス度を確認することで、住宅選びや移動手段の検討に役立ててください。また、本サイトで使用しているデータの出典と加工内容についても記載していますので、ご参照ください。
        """
    )

    district, stop, route = read_and_process_data()
    district, stop, route = filter_by_cluster(district, stop, route, ["白石", "大殿", "湯田"])
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
