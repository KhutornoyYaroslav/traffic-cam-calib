import numpy as np
from glob import glob
from sklearn.cluster import KMeans
from core.vehicle.vehicle import Vehicle


def main():
    # load models
    model_paths = sorted(glob("data/models/*"))
    vehicles = []
    for path in model_paths:
        vehicle = Vehicle(tag=path)
        vehicle.load(path)
        vehicles.append(vehicle)

    # get vehicle points
    vehicles_points = []
    for vehicle in vehicles:
        assert vehicle.points_count() == 32
        pts = vehicle.get_obj_pts(centered=False)
        sorted_keys = sorted(list(pts.keys()))
        sorted_pts = {key: pts[key] for key in sorted_keys}
        vehicles_points.append(list(sorted_pts.values()))
    vehicles_points = np.array(vehicles_points) # (N, 32, 3)
    vehicles_norms = np.linalg.norm(vehicles_points, axis=-1) # (N, 32)

    # clusterize
    n_clusters = 5
    solver = KMeans(n_clusters=n_clusters, init='random', tol=1e-3, max_iter=300, verbose=0)
    result = solver.fit(vehicles_norms)

    cluster_idxs = []
    for cluster_id in range(n_clusters):
        idxs = [idx for idx in range(len(result.labels_)) if result.labels_[idx] == cluster_id]
        cluster_idxs.append(idxs)

    # show result
    for cluster_id, vehicle_idxs in enumerate(cluster_idxs):
        print(f"Cluster {cluster_id} models num: {len(vehicle_idxs)}")

    # print(result.labels_)
    # print(result.n_features_in_)


if __name__ == "__main__":
    main()
