import numpy as np
from glob import glob
from sklearn.cluster import KMeans
from core.objects.carskeleton import CarSkeleton


def main():
    # load models
    model_paths = sorted(glob("data/models/*"))
    cars = []
    for path in model_paths:
        car = CarSkeleton(tag=path)
        car.load(path)
        cars.append(car)

    # get vehicle points
    cars_points = []
    for car in cars:
        assert car.points_count() == 32
        pts = car.keypoints_xyz
        c = car.get_centroid()

        sorted_keys = sorted(list(pts.keys()))
        sorted_pts = {key: pts[key] for key in sorted_keys}

        for key in sorted_pts.keys():
            sorted_pts[key] -= c

        cars_points.append(list(sorted_pts.values()))
    cars_points = np.array(cars_points) # (N, 32, 3)
    cars_norms = np.linalg.norm(cars_points, axis=-1) # (N, 32)

    # clusterize
    n_clusters = 4
    solver = KMeans(n_clusters=n_clusters, init='random', tol=1e-3, max_iter=300, verbose=1)
    result = solver.fit(cars_norms)

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
