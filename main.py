from PIL import Image
from collections import defaultdict
from random import random
import math
import sys


if len(sys.argv) < 4:
    print(f"usage: {sys.argv[0]} <file> <cluster count> <iteration count>")
    sys.exit(1)
filename = sys.argv[1]
cluster_count = int(sys.argv[2])
iter_count = int(sys.argv[3])


class Color:
    def __init__(self, color, count):
        r, g, b = color
        self.color = (r / 256, g / 256, b / 256)
        self.count = count

    def __equals__(self, other):
        if self.color != other.color:
            return False
        return True


def euclid_distance(centroid, point):
    r1, g1, b1 = centroid
    r2, g2, b2 = point.color
    rd, gd, bd = r1 - r2, g1 - g2, b1 - b2
    return math.sqrt(rd * rd + gd * gd + bd * bd)


def calc_closest_centroid(centroids, point):
    min_i, min_dist = 0, math.inf
    for i, centroid in enumerate(centroids):
        new_dist = euclid_distance(centroid, point)
        if new_dist < min_dist:
            min_dist = new_dist
            min_i = i
    return min_i, centroids[min_i]


def calc_clusters(centroids, points):
    clusters = [[] for c in centroids]
    for point in points:
        i, _ = calc_closest_centroid(centroids, point)
        clusters[i].append(point)
    return clusters


def calc_centroids(clusters):
    centroids = []
    for cluster in clusters:
        r, g, b = 0, 0, 0
        count = 0
        for point in cluster:
            count += point.count
            r += point.color[0] * point.count
            g += point.color[1] * point.count
            b += point.color[2] * point.count
        if count == 0:
            continue
        r /= count
        g /= count
        b /= count
        centroids.append((r, g, b))
    return centroids


print("Opening image")
img = Image.open(filename)
img = img.convert("RGB")
pixels = img.load()

points_dict = defaultdict(int)

print("Mapping image to points")
for x in range(img.width):
    for y in range(img.height):
        points_dict[pixels[x, y]] += 1

points = []
for k, v in points_dict.items():
    points.append(Color(k, v))

centroids = [(random(), random(), random()) for i in range(cluster_count)]

for i in range(iter_count):
    try:
        print(f"\rIterating: {i+1:>{len(str(iter_count))}}/{iter_count}", end="")
        clusters = calc_clusters(centroids, points)
        centroids = calc_centroids(clusters)
    except KeyboardInterrupt:
        break
print()

colors = dict()

print("Mapping points to image")
for point, count in points_dict.items():
    _, centroid = calc_closest_centroid(centroids, Color(point, count))
    r, g, b = centroid
    r = math.floor(r * 256)
    g = math.floor(g * 256)
    b = math.floor(b * 256)
    colors[point] = (r, g, b)

print("Writing image")
for x in range(img.width):
    for y in range(img.height):
        try:
            pixels[x, y] = colors[pixels[x, y]]
        except KeyError:
            print(f"Failed to get color map at ({x}, {y})")

print(f"Clusters: {len(centroids)}")
img.show()
