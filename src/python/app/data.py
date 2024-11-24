import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np


BUS_STOP_PATH = "data/bus/C0604_バスの状況/GIS/C06041_H22_バス停の状況_OP.shp"
BUS_ROUTE_PATH = "data/bus/C0604_バスの状況/GIS/C06042_H22_バス路線の状況_OP.shp"
TRAIN_STATION_PATH = "data/train/C0603_鉄道・路面電車等の状況/GIS/C06031_R03_駅の状況_OP.shp"
TRAIN_ROUTE_PATH = "data/train/C0603_鉄道・路面電車等の状況/GIS/C06032_R03_路線の状況_OP.shp"
STOP_COLUMNS = ["NAME", "HINDO", "ROSEN", "TYPE", "geometry"]
ROUTE_COLUMNS = ["TYPE", "geometry"]
DISTRICT_PATH = "data/district/B002005212020DDSWC35203/r2kb35203.shp"
DISTRICT_COLUMNS = ["S_NAME", "geometry"]


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
    district = gpd.read_file("data/district/B002005212020DDSWC35203/r2kb35203.shp")
    district = district[DISTRICT_COLUMNS]
#   district = district[district.KIHON1.astype(float) < 400]
    return district


# smooth saturation function
# citation: https://ieeexplore.ieee.org/document/9997143
def smooth_saturation(x: np.ndarray, alpha: float = 0.05, max: float = 1.0) -> np.ndarray:
    return (x + max - np.sqrt(alpha + (x - max) ** 2)) / 2


def eval_score(district: gpd.GeoDataFrame, stop: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    st_point = stop.to_crs(epsg=3098).geometry
    st_point = np.array([(point.x, point.y) for point in st_point])
    district_centroid = district.to_crs(epsg=3098).centroid
    district_centroid = np.array([(point.x, point.y) for point in district_centroid])
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(st_point)
    distance, idx = nn.kneighbors(district_centroid)

    idx = idx.flatten()
    distance = distance.flatten()
    hindo = stop["HINDO"][idx].to_numpy()
    # score is scaled for simplicity
#   hindo = np.array([100, 24, 12, 6])
#   distance = np.array([10, 400, 800, 1600])
#   hindo, distance = np.meshgrid(hindo, distance)
#   hindo = hindo.flatten()
#   distance = distance.flatten()
    # hindo = 24 = 1 / 30min * 12h
    # distance = 400 = 5km/h * 10min
    score = 10 * smooth_saturation(hindo / 24) * smooth_saturation(400 / (distance + 1e-6))
#   for h, d, s in zip(hindo, distance, score):
#       print(f"hindo: {h}, distance: {d}, score: {s:.2f}")

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

if __name__ == "__main__":
    district, stop, route = read_and_process_data()
    print(district.head())
