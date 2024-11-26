from django.db.models import Q  # Correctly import Q for query building
from django.shortcuts import render
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Products


def tfidf_search(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    if not query:
        return render(request, 'search_results.html', {'query': query, 'results': []})

    # Fetch all products with non-empty descriptions
    products = Products.objects.exclude(description__isnull=True).exclude(description__exact='')
    if not products:
        return render(request, 'search_results.html', {'query': query, 'results': []})

    # Extract product descriptions
    descriptions = [product.description for product in products]

    # Add the query to the descriptions for vectorization
    descriptions.append(query)

    # Compute TF-IDF matrix
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    # Calculate cosine similarity of the query with all product descriptions
    query_vector = tfidf_matrix[-1]  # The last row corresponds to the query
    product_vectors = tfidf_matrix[:-1]  # All rows except the last are product descriptions
    similarity_scores = cosine_similarity(query_vector, product_vectors).flatten()

    # Pair products with their similarity scores
    product_similarity = list(zip(products, similarity_scores))

    # Sort products by similarity score (highest first)
    sorted_products = sorted(product_similarity, key=lambda x: x[1], reverse=True)

    # Filter results with a minimum similarity threshold (optional)
    results = [product for product, score in sorted_products if score > 0]

    return render(request, 'search_results.html', {'query': query, 'results': results})
def home(request):
    return render(request, 'search.html')


