from django.db.models import Q

from .models import Products
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime


import os
import numpy as np
import cv2
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt


def image_similarity_search(
    image_folder="core/product_images",
    query_image_path="core/product_images/product_2_image1.jpg",
    bins=(16, 16, 16),
    top_n=5,
):
    def get_products_for_paths(image_paths):
        products = Products.objects.filter(
            Q(image1_url__in=image_paths)
            | Q(image2_url__in=image_paths)
            | Q(image3_url__in=image_paths)
        )
        return products

    def remove_background(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        result = cv2.bitwise_and(image, image, mask=mask)
        return result

    def extract_features(image_path, bins=(16, 16, 16)):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error reading image: {image_path}")
            return None
        image = remove_background(image)
        image = cv2.resize(image, (256, 256))
        hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        return hist

    def build_feature_database(image_folder):
        features = []
        image_paths = []
        for filename in os.listdir(image_folder):
            if filename.endswith(".jpg"):
                path = os.path.join(image_folder, filename)
                print(f"Processing {filename}...")
                feature = extract_features(path)
                if feature is not None:
                    image_paths.append(path)
                    features.append(feature)
        return np.array(features), image_paths

    def search_similar_images(query_image_path, features, image_paths, top_n=5):
        query_features = extract_features(query_image_path)
        if query_features is None:
            print("Error processing query image.")
            return []
        distances = cdist([query_features], features, metric="euclidean")[0]
        sorted_indices = np.argsort(distances)
        results = [(image_paths[idx], distances[idx]) for idx in sorted_indices]
        return results[:top_n]

    def display_results(query_image_path, results):
        query_image = cv2.imread(query_image_path)
        query_image = cv2.cvtColor(query_image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(15, 5))
        plt.subplot(1, len(results) + 1, 1)
        plt.imshow(query_image)
        plt.title("Query Image")
        plt.axis("off")
        for i, (path, distance) in enumerate(results):
            result_image = cv2.imread(path)
            result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            plt.subplot(1, len(results) + 1, i + 2)
            plt.imshow(result_image)
            plt.title(f"Dist: {distance:.2f}")
            plt.axis("off")
        plt.show()

    # Main function logic
    print("Building feature database...")
    features, image_paths = build_feature_database(image_folder)

    print("Searching for similar images...")
    results = search_similar_images(query_image_path, features, image_paths, top_n)
    ids = []
    for tup in results:
        stri = tup[0]
        id = stri[28]
        if stri[29].isdigit():
            id += stri[29]
        ids.append(id)
        id = ""
    print(ids)

    return ids


def get_combined_descriptions():
    # Retrieve all product descriptions and concatenate them into a single string
    products = Products.objects.all()
    combined_description = " ".join(product.description for product in products)
    print(combined_description)
    return combined_description


def recommend_filters(previous_orders):
    """
    Generate intelligent recommendations for product filters based on previous orders.
    :param previous_orders: Queryset of PreviousOrders objects.
    :return: A dictionary of recommended filters.
    """
    if not previous_orders.exists():
        return {"message": "No previous orders found. Recommendations unavailable."}

    # Extract attribute data from previous orders
    attributes = {
        "gender": [],
        "color": [],
        "fabric": [],
        "activity": [],
        "fit": [],
        "length": [],
        "category": [],
        "price": [],
    }

    for order in previous_orders:
        product = order.product
        attributes["gender"].append(product.gender)
        attributes["color"].append(product.color)
        attributes["fabric"].append(product.fabric)
        attributes["activity"].append(product.activity)
        attributes["fit"].append(product.fit)
        attributes["length"].append(product.length)
        attributes["category"].append(product.category)
        attributes["price"].append(product.price)

    # 1. Frequency Analysis
    recommendations = {}
    for key, values in attributes.items():
        if key == "price":
            # Compute price statistics
            prices = np.array(values)
            recommendations["price_range"] = {
                "min": round(np.min(prices), 2),
                "max": round(np.max(prices), 2),
                "avg": round(np.mean(prices), 2),
            }
        else:
            counter = Counter(values)
            top_choices = counter.most_common(3)  # Top 3 most common filters
            recommendations[key] = [choice[0] for choice in top_choices if choice[0]]

    # 2. Clustering for Diversity
    try:
        # Create feature vectors for clustering (skip price)
        feature_vectors = []
        for i in range(len(attributes["gender"])):
            vector = [
                hash(attributes["gender"][i]) % 100,
                hash(attributes["color"][i]) % 100,
                hash(attributes["fabric"][i]) % 100,
                hash(attributes["activity"][i]) % 100,
                hash(attributes["fit"][i]) % 100,
                hash(attributes["length"][i]) % 100,
                hash(attributes["category"][i]) % 100,
            ]
            feature_vectors.append(vector)

        feature_vectors = np.array(feature_vectors)

        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=min(3, len(feature_vectors)), random_state=0)
        clusters = kmeans.fit_predict(feature_vectors)

        # Find a diverse recommendation from each cluster
        cluster_recommendations = []
        for cluster_idx in range(max(clusters) + 1):
            indices = np.where(clusters == cluster_idx)[0]
            cluster_recommendations.append(attributes["category"][indices[0]])

        recommendations["diverse_categories"] = list(set(cluster_recommendations))

    except Exception as e:
        recommendations["clustering_error"] = str(e)

    # 3. Seasonal/Time-Based Suggestions
    current_month = datetime.now().month
    if current_month in [12, 1, 2]:
        recommendations["seasonal"] = ["Sweaters", "Long Sleeve Shirts", "Wool"]
    elif current_month in [6, 7, 8]:
        recommendations["seasonal"] = ["Tank Tops", "Shorts", "Cotton"]
    else:
        recommendations["seasonal"] = ["T-Shirts", "Pima Cotton", "Casual"]

    return recommendations


def filter_extractor(query):
    products = Products.objects.all()
    filters = set()

    for product in products:
        filters.add(product.activity)
        filters.add(product.color)
        filters.add(product.gender)
        filters.add(product.category)

    returnable_filters = []
    query_words = set(word.lower() for word in query.split())

    for filter_value in filters:
        if filter_value.lower() in query_words:
            returnable_filters.append(filter_value)

    return returnable_filters
