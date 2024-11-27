from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Products
from django.http import JsonResponse
import json


def tfidf_search(query):

    if not query:
        return JsonResponse({"query": query, "results": []}, safe=False)

    products = Products.objects.all()
    if not products.exists():
        return JsonResponse({"query": query, "results": []}, safe=False)

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

    results = [
        {
            "id": product.id,
            "name": product.name,
            "color": product.color,
            "price": str(
                product.price
            ),  # Convert Decimal to string for JSON serialization
            "gender": product.gender,
            "category": product.category,
            "length": product.length,
            "fit": product.fit,
            "activity": product.activity,
            "fabric": product.fabric,
            "description": product.description,
            "image1_url": product.image1_url,
            "image2_url": product.image2_url,
            "image3_url": product.image3_url,
            "similarity_score": score,  # Include similarity score for debugging/relevance
        }
        for product, score in sorted_products
        if score > 0
    ][:10]

    return {"query": query, "results": results}
