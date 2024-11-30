from .models import Products

def get_combined_descriptions():
    # Retrieve all product descriptions and concatenate them into a single string
    products = Products.objects.all()
    combined_description = " ".join(product.description for product in products)
    print(combined_description)
    return combined_description


from django.db.models import Q

from decimal import Decimal

def recommend_similar_products(previous_orders):
    """
    This function takes a queryset of `PreviousOrders` and recommends similar products.

    Args:
        previous_orders: A queryset of `PreviousOrders` objects representing the user's previous purchases.

    Returns:
        A queryset of `Products` objects containing recommended products.
    """

    # Get a list of product IDs from previous orders
    previous_order_product_ids = [order.product.id for order in previous_orders]

    # Exclude previously purchased products from recommendations
    exclude_products = Q(pk__in=previous_order_product_ids)

    # Define similarity filters based on product attributes
    filters = Q()
    for order in previous_orders:
        product = order.product

        # Add filters based on available attributes
        filters |= Q(
            Q(gender=product.gender) | Q(category=product.category),
            Q(length=product.length),
            Q(fit=product.fit),
            Q(color=product.color),
            Q(activity=product.activity),
            Q(fabric=product.fabric),
            # Adjust price range based on your preference, ensuring decimal precision
            Q(price__gte=product.price * Decimal('0.8')),
            Q(price__lte=product.price * Decimal('1.2')),
        )

    # Combine filters and exclude previously purchased items
    recommended_products = Products.objects.filter(filters).exclude(exclude_products)

    # Order recommendations (optional)
    # recommended_products = recommended_products.order_by('-price')  # Order by descending price

    return recommended_products