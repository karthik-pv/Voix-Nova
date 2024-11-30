from .models import Products

def get_combined_descriptions():
    # Retrieve all product descriptions and concatenate them into a single string
    products = Products.objects.all()
    combined_description = " ".join(product.description for product in products)
    print(combined_description)
    return combined_description




from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime

def recommend_filters(previous_orders):
    """
    Generate intelligent recommendations for product filters based on previous orders.
    :param previous_orders: Queryset of PreviousOrders objects.
    :return: A dictionary of recommended filters.
    """
    if not previous_orders.exists():
        return {
            "message": "No previous orders found. Recommendations unavailable."
        }

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

# Usage Example
# previous_orders = PreviousOrders.objects.all()
# filters = recommend_filters(previous_orders)
# print(filters)

