from .models import Products

def get_combined_descriptions():
    # Retrieve all product descriptions and concatenate them into a single string
    products = Products.objects.all()
    combined_description = " ".join(product.description for product in products)
    print(combined_description)
    return combined_description


get_combined_descriptions()