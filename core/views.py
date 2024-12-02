from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from .models import Products, Cart, PreviousOrders
from .ai_model import GeminiClient
from .serializers import ProductSerializer
from .tfidf import tfidf_search
from rest_framework.decorators import api_view
import json
from django.views.decorators.csrf import csrf_exempt

from .utils import image_similarity_search, filter_extractor

from .utils import image_similarity_search, filter_extractor, recommend_filters


ai = GeminiClient()
filter_var = []
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def recommendations_view(request):
    """
    API endpoint to return product filter recommendations.
    :param request: HTTP request.
    :return: JsonResponse with the recommendations.
    """
    results = recommend_filters()
    return JsonResponse(
        {
            "frequency_based_products": results[0],
            "seasonal_based_products": results[1],
        },
        safe=False,
    )


@csrf_exempt
def image_similarity_view(request):
    if request.method == "POST":
        try:
            # Check if an image is provided in the request
            if "image" not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            # Save the uploaded image to a temporary directory
            uploaded_image = request.FILES["image"]
            temp_image_path = default_storage.save(
                f"temp/{uploaded_image.name}", ContentFile(uploaded_image.read())
            )

            # Define the folder containing product images
            image_folder = "core/product_images"

            # Run the similarity search
            ids = image_similarity_search(
                image_folder=image_folder,
                query_image_path=temp_image_path,
                bins=(16, 16, 16),
                top_n=7,
            )

            # Cleanup: Remove the temporary image after processing
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            ids = list(set(ids))
            ids = ids[:3]
            # Fetch products with IDs in the given list
            products = Products.objects.filter(id__in=ids)

            # Convert products to a list of dictionaries (for JSON response)
            product_list = [
                {
                    "id": product.id,
                    "name": product.name,
                    "color": product.color,
                    "price": float(
                        product.price
                    ),  # Converting Decimal to float for JSON serialization
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
                }
                for product in products
            ]

            return JsonResponse({"products": product_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def filter_reset(request):
    if request.method == "GET":
        global filter_var
        filter_var.clear()
        return JsonResponse(
            {"message": "Filter reset successfully", "filters": filter_var}, status=200
        )
    return JsonResponse({"message": "Inavlid request"})


def home_page_conversationalist(request):
    if request.method == "GET":
        transcript = ai.home_page()
        return JsonResponse({"message": transcript})
    return JsonResponse({"message": "Invalid request"})


def home(request):
    similar_products = image_similarity_search()
    print(len(similar_products))
    print(similar_products)
    return render(request, "search.html")


def home_page_conversationalist(request):
    if request.method == "GET":
        transcript = ai.home_page()
        return JsonResponse({"message": transcript})
    return JsonResponse({"message": "Invalid request"})


def product_list_page_conversationalist(request):
    if request.method == "GET":
        query = request.GET.get("search")
        transcript = ai.product_list_page(query)
        return JsonResponse({"message": transcript})
    return JsonResponse({"message": "Invalid request"})


def filter_conversationalist(request):
    global filter_var
    if request.method == "GET":
        query = request.GET.get("filterMsg")
        transcript = ai.filtering_interaction(query, filter_var)
        filter_extractor(query, filter_var)
        return JsonResponse({"message": transcript, "filters": filter_var})
    return JsonResponse({"message": "Invalid request"})


def product_details_page_conversationalist(request):
    if request.method == "GET":
        query = request.GET.get("search")
        transcript = ai.product_details_page(query)
        return JsonResponse({"message": transcript})
    return JsonResponse({"message": "Invalid request"})


def product_description_conversationalist(request):
    if request.method == "GET":
        query = request.GET.get("search")
        transcript = ai.product_description(query)
        return JsonResponse({"message": transcript})
    return JsonResponse({"message": "Invalid request"})


def get_all_products(request):
    print("here")
    products = Products.objects.all()
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)


def group_search_view(request):
    query = request.GET.get("q", "")
    print(f"Search Query: {query}")
    results = tfidf_search(query)
    relevant_data = str(results["results"])
    print(len(results["results"]))
    return JsonResponse(
        {
            "query": query,
            "results": results.get("results", []),
        },
        safe=False,
    )


def particular_search_view(request):
    query = request.GET.get("q", "")
    print(f"Search Query: {query}")
    results = tfidf_search(query)
    temp = results["results"]
    results["results"] = temp[0]
    return JsonResponse(
        {
            "query": query,
            "results": results.get("results", []),
        },
        safe=False,
    )


def add_to_cart(request):
    if request.method == "GET":
        query = request.GET.get("q", "")
        print(f"Search Query bsias: {query}")

        # Perform the search
        results = tfidf_search(query)["results"]

        if not results:
            return JsonResponse(
                {"message": "No products found to add to cart"}, status=404
            )

        add_to_cart_id = results[0]["id"]
        product = Products.objects.get(id=add_to_cart_id)
        cart_item = Cart(product=product)
        cart_item.save()

        # Serialize the product data to return
        product_data = ProductSerializer(product).data
        return JsonResponse(
            {"message": "Added to cart", "product": product_data}, status=201
        )
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)


def finalize_cart(request):
    # Ensure the request method is GET
    if request.method == "GET":
        # Retrieve all cart items
        cart_items = Cart.objects.all()

        if not cart_items.exists():
            return JsonResponse(
                {"total_cost": 0.0, "message": "Cart is empty."}, status=200
            )

        # Initialize total cost
        total_cost = 0.0

        # Move products from cart to previous orders and calculate total cost
        for cart_item in cart_items:
            total_cost += float(
                cart_item.product.price
            )  # Assuming price is a Decimal or float

            # Create a PreviousOrders entry for each product
            PreviousOrders.objects.create(product=cart_item.product)

        # Clear the cart by deleting all cart items
        cart_items.delete()
        message = ai.checkout_cart(total_cost)
        # Return the total cost as a JSON response
        return JsonResponse({"message": message}, status=200)

    # If the request method is not GET, return an error response
    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_cart_products(request):
    if request.method == "GET":
        # Retrieve all cart items
        cart_items = Cart.objects.all()

        if not cart_items.exists():
            return JsonResponse({"cart": [], "message": "Cart is empty."}, status=200)

        # Serialize the products in the cart using ProductSerializer
        products = [cart_item.product for cart_item in cart_items]
        serialized_products = ProductSerializer(products, many=True).data

        return JsonResponse({"cart": serialized_products}, status=200)

    # If the request method is not GET, return an error response
    return JsonResponse({"error": "Invalid request method"}, status=400)


def recommendations_conversationalist(request):
    if request.method == "GET":
        transcript = ai.recommendation_page(str(recommend_filters()))
        return JsonResponse({"message": transcript}, status=200)
    return JsonResponse({"message": "Invalid request"})


def cart_conversationalist(request):
    if request.method == "GET":
        cart_items = Cart.objects.all()
        products = [cart_item.product for cart_item in cart_items]
        serialized_products = ProductSerializer(products, many=True).data
        transcript = ai.cart_page(str(serialized_products), str(recommend_filters()))
        return JsonResponse({"message": transcript}, status=200)
    return JsonResponse({"message": "Invalid request"})
