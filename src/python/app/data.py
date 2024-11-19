import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import numpy as np


def load_bus_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
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
    return bus_stop, bus_route


def load_district_data() -> gpd.GeoDataFrame:
    district = gpd.read_file("data/district/B002005212020DDSWC35203/r2kb35203.shp")
#   district = district[district.KIHON1.astype(float) < 400]
    return district


def smooth_saturation(x: np.ndarray, alpha: float = 0.05, max: float = 1.0) -> np.ndarray:
    return (x + max - np.sqrt(alpha + (x - max) ** 2)) / 2


def get_score(district: gpd.GeoDataFrame, bus_stop: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    bs_point = bus_stop.to_crs(epsg=3098).geometry
    bs_point = np.array([(point.x, point.y) for point in bs_point])
    district_centroid = district.to_crs(epsg=3098).centroid
    district_centroid = np.array([(point.x, point.y) for point in district_centroid])
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(bs_point)
    distance, idx = nn.kneighbors(district_centroid)

    idx = idx.flatten()
    distance = distance.flatten()
    hindo = bus_stop["hindo"][idx].to_numpy()
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

    district["bus_stop"] = bus_stop["B_NAME"][idx].values
    district["distance"] = distance
    district["hindo"] = hindo
    district["score"] = score
    return district


if __name__ == "__main__":
    bus_stop, bus_route = load_bus_data()
    district = load_district_data()
    district = get_score(district, bus_stop)
    print(district.head())
