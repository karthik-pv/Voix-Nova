from django.db.models import Q  # Correctly import Q for query building
from django.shortcuts import render
from django.http import JsonResponse
from .models import Products
from .ai_model import GeminiClient
from .serializers import ProductSerializer
from .tfidf import tfidf_search


def home(request):
    return render(request, "search.html")


def group_search_view(request):
    query = request.GET.get("q", "")
    print(f"Search Query: {query}")
    results = tfidf_search(query)
    print(len(results["results"]))
    return JsonResponse(
        {"query": query, "results": results.get("results", [])}, safe=False
    )


def particular_search_view(request):
    query = request.GET.get("q", "")
    print(f"Search Query: {query}")
    results = tfidf_search(query)
    temp = results["results"]
    results["results"] = temp[0]
    return JsonResponse(
        {"query": query, "results": results.get("results", [])}, safe=False
    )
