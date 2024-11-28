import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


BUS_STOP_PATH = "data/bus/C0604_バスの状況/GIS/C06041_H22_バス停の状況_OP.shp"
BUS_ROUTE_PATH = "data/bus/C0604_バスの状況/GIS/C06042_H22_バス路線の状況_OP.shp"
TRAIN_STATION_PATH = "data/train/C0603_鉄道・路面電車等の状況/GIS/C06031_R03_駅の状況_OP.shp"
TRAIN_ROUTE_PATH = "data/train/C0603_鉄道・路面電車等の状況/GIS/C06032_R03_路線の状況_OP.shp"
STOP_COLUMNS = ["NAME", "HINDO", "ROSEN", "TYPE", "geometry"]
ROUTE_COLUMNS = ["TYPE", "geometry"]
DISTRICT_PATH = "data/district/B002005212020DDSWC35203/r2kb35203.shp"
DISTRICT_COLUMNS = ["S_NAME", "geometry", "cluster"]
SCORE_MAX = 10
HINDO_MAX = 144  # 144 / day = 1 / 5 min * 12 h
HINDO_MIN = 0.5
DISTANCE_MAX = 2400  # 1200 m = 5 km/h * 60 min
DISTANCE_MIN = 40  # 40 m = 5 km/h * 1 min


def get_b_hindo(stop: gpd.GeoDataFrame, route: gpd.GeoDataFrame, buffer_m: float = 10) -> list[float]:
    st_bufferd = stop.to_crs(epsg=3098).buffer(buffer_m)
    rt_geometry = route.to_crs(epsg=3098).geometry

    hindo = []
    for st in st_bufferd:
        is_intersected = rt_geometry.intersects(st)
        hindo.append(route[is_intersected]["B_HINDO"].max())
    return hindo


def load_stop_route(stop_path: str, route_path: str) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    stop = gpd.read_file(stop_path, encoding="shift-jis")
    route = gpd.read_file(route_path, encoding="shift-jis")
    return stop, route


def load_bus_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    stop, route = load_stop_route(BUS_STOP_PATH, BUS_ROUTE_PATH)
    stop = stop.rename(columns={"B_NAME": "NAME", "B_ROSEN": "ROSEN"})
    stop["HINDO"] = get_b_hindo(stop, route)
    stop["TYPE"] = "bus"
    stop = stop[STOP_COLUMNS]
    route["TYPE"] = "bus"
    route = route[ROUTE_COLUMNS]
    return stop, route


def load_train_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    stop, route = load_stop_route(TRAIN_STATION_PATH, TRAIN_ROUTE_PATH)
    stop = stop.rename(columns={"EKI_NAME": "NAME", "T_HIND": "HINDO", "T_ROSEN": "ROSEN"})
    stop["TYPE"] = "train"
    stop = stop[STOP_COLUMNS]
    route["TYPE"] = "train"
    route = route[ROUTE_COLUMNS]
    return stop, route


def load_district_data() -> gpd.GeoDataFrame:
    district = gpd.read_file(DISTRICT_PATH)
    district["cluster"] = "白石"
    # S_NAMEが'大内'から始まる単語ならば、clusterに'大内'に設定し、それ以外は変更しない
    dict_cluster = {
        "大内": "大内",
        "宮島町": "大内",
        "上小鯖": "小鯖",
        "下小鯖": "小鯖",
        "仁保": "仁保",
        "平井": "平川",
        "黒川": "平川",
        "吉田": "平川",
        "小郡": "小郡",
        "陶": "陶",
        "名田島": "名田島",
        "鋳銭司": "鋳銭司",
        "阿知須": "阿知須",
        "秋穂二島": "秋穂二島",
        "秋穂東": "秋穂",
        "秋穂西": "秋穂",
        "徳地": "徳地",
        "阿東": "阿東",
        "吉敷": "吉敷",
        "維新公園": "吉敷",
        "中尾": "吉敷",
        "朝田": "大歳",
        "矢原": "大歳",
        "今井町": "大歳",
        "富田原町": "大歳",
        "周布町": "大歳",
        "若宮町": "大歳",
        "幸町": "大歳",
        "宝町": "大歳",
        "穂積町": "大歳",
        "葵一丁目": "大歳",
        "葵二丁目": "大歳",
        "天花": "大殿",
        "上天花町": "大殿",
        "香山町": "大殿",
        "木町": "大殿",
        "野田": "大殿",
        "堂の前町": "大殿",
        "金古曽町": "大殿",
        "円政寺": "大殿",
        "新馬場": "大殿",
        "道祖町": "大殿",
        "石観音町": "大殿",
        "古熊": "大殿",
        "滝町": "大殿",
        "大手町": "大殿",
        "春日町": "大殿",
        "上竪小路": "大殿",
        "下竪小路": "大殿",
        "久保小路": "大殿",
        "銭湯小路": "大殿",
        "諸願小路": "大殿",
        "後河原": "大殿",
        "水の上町": "大殿",
        "八幡馬場": "大殿",
        "大市町": "大殿",
        "大殿大路": "大殿",
        "三の宮": "大殿",
        "上宇野令": "大殿",
        "宮野": "宮野",
        "江良": "宮野",
        "桜畠": "宮野",
        "平野": "宮野",
        "折本": "宮野",
        "芝崎町": "宮野",
        "青葉台": "宮野",
        "七尾台": "宮野",
        "緑ヶ丘": "宮野",
        "湯田": "湯田",
        "前町": "湯田",
        "朝倉町": "湯田",
        "元町": "湯田",
        "下市町": "湯田",
        "熊野町": "湯田",
        "赤妻町": "湯田",
        "泉町": "湯田",
        "錦町": "湯田",
        "楠木町": "湯田",
        "神田町": "湯田",
        "荻町": "湯田",
        "泉都町": "湯田",
        "松美町": "湯田",
        "三和町": "湯田",
        "下宇野令": "湯田",
        "嘉川": "嘉川",
        "江崎": "嘉川",
        "深溝": "嘉川",
        "佐山": "佐山",
    }
    for k, v in dict_cluster.items():
        district.loc[district.S_NAME.str.startswith(k), 'cluster'] = v
    district = district[DISTRICT_COLUMNS]
    return district


# smooth saturation function
# citation: https://ieeexplore.ieee.org/document/9997143
def smooth_saturation(x: np.ndarray, alpha: float = 0.001, max: float = 1.0, min: float = 0.0) -> np.ndarray:
    return (max - np.sqrt(alpha + (x - max) ** 2)) / 2 + \
           (min + np.sqrt(alpha + (x - min) ** 2)) / 2


def score_func(x: np.ndarray, min: float = 1.0, max: float = 10.0) -> np.ndarray:
    x = np.log(x / min) / np.log(max / min)
    return smooth_saturation(x)


def eval_score(district: gpd.GeoDataFrame, stop: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    st_point = stop.to_crs(epsg=3098).geometry
    st_point = np.array([(point.x, point.y) for point in st_point])
    district_centroid = district.to_crs(epsg=3098).centroid
    district_centroid = np.array([(point.x, point.y) for point in district_centroid])
    nn = NearestNeighbors(n_neighbors=5)
    nn.fit(st_point)
    distance, idx = nn.kneighbors(district_centroid)

    hindo = stop["HINDO"].to_numpy()[idx]
    score_h = score_func(hindo, min=HINDO_MIN, max=HINDO_MAX)
    score_d = 1 - score_func(distance, min=DISTANCE_MIN, max=DISTANCE_MAX)
    score = SCORE_MAX * np.sqrt(score_h * score_d)
    idx_neighbour = np.argmax(score, axis=1)
    idx = idx[np.arange(idx.shape[0]), idx_neighbour]
    hindo = hindo[np.arange(hindo.shape[0]), idx_neighbour]
    distance = distance[np.arange(distance.shape[0]), idx_neighbour]
    score = score[np.arange(score.shape[0]), idx_neighbour]

    district["name"] = stop["NAME"][idx].values
    district["type"] = stop["TYPE"][idx].values
    district["distance"] = distance
    district["hindo"] = hindo
    district["score"] = score
    return district


def read_and_process_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    bus_stop, bus_route = load_bus_data()
    train_stop, train_route = load_train_data()
    stop = gpd.GeoDataFrame(pd.concat([bus_stop, train_stop], ignore_index=True))
    route = gpd.GeoDataFrame(pd.concat([bus_route, train_route], ignore_index=True))
    district = load_district_data()
    district = eval_score(district, stop)
    return district, stop, route


def filter_by_cluster(
        district: gpd.GeoDataFrame,
        stop: gpd.GeoDataFrame,
        route: gpd.GeoDataFrame,
        clusters: list[str],
        ) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    district = district[district["cluster"].isin(clusters)]
    district_geometry = district.to_crs(epsg=3098).union_all().buffer(100)
    stop = stop[stop.to_crs(epsg=3098).geometry.within(district_geometry)]
    route = route[route.to_crs(epsg=3098).geometry.within(district_geometry)]
    return district, stop, route


def plot_score_hist(district: gpd.GeoDataFrame, key: str = "score", range: tuple[float] | None = None) -> None:
    _, ax = plt.subplots()
    ax.hist(district[key], bins="auto", range=range)
    ax.set_xlabel(key)
    ax.set_ylabel("count")
    plt.show()


if __name__ == "__main__":
    district, stop, route = read_and_process_data()
    print(district.cluster.value_counts())
    print(district.shape, stop.shape, route.shape)
    print(f"{len(district)} districts, {len(stop)} stops, {len(route)} routes")
    district, stop, route = filter_by_cluster(district, stop, route, ["白石", "大殿", "湯田"])
    print(f"{len(district)} districts, {len(stop)} stops, {len(route)} routes")
    print(district["score"].describe())
#   plot_score_hist(district, key="score")
