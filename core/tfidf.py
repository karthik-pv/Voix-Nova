from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Products
from django.http import JsonResponse
import json

from .serializers import ProductSerializer

global returnable_list

def tfidf_search(query):
    global returnable_list
    if not query:
        return {"query": query, "results": []}

    products = Products.objects.all()
    if not products.exists():
        return {"query": query, "results": []}

    descriptions = [product.description for product in products]
    descriptions.append(query)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    query_vector = tfidf_matrix[-1]  # The last row corresponds to the query
    product_vectors = tfidf_matrix[
        :-1
    ]  # All rows except the last are product descriptions
    similarity_scores = cosine_similarity(query_vector, product_vectors).flatten()

    product_similarity = list(zip(products, similarity_scores))
    sorted_products = sorted(product_similarity, key=lambda x: x[1], reverse=True)
    if len(sorted_products):
        returnable_list = sorted_products
    results = [
        ProductSerializer(product).data  # Use the serializer here
        for product, score in returnable_list
        if score > 0
    ][:10]

    return {"results": results}
