from django.db import models


class Products(models.Model):
    # Gender Choices
    GENDER_CHOICES = [
        ("Women", "Women"),
        ("Men", "Men"),
    ]

    # Category Choices
    CATEGORY_CHOICES = [
        ("Bodysuits", "Bodysuits"),
        ("Long Sleeve Shirts", "Long Sleeve Shirts"),
        ("Shirts", "Shirts"),
        ("T-Shirts", "T-Shirts"),
        ("Tank Tops", "Tank Tops"),
    ]

    # Collection Choice

    # Length Choices
    LENGTH_CHOICES = [
        ("Cropped", "Cropped"),
        ("Long", "Long"),
        ("Short", "Short"),
    ]

    # Fit Choices
    FIT_CHOICES = [
        ("Classic Fit", "Classic Fit"),
        ("Relaxed Fit", "Relaxed Fit"),
        ("Slim Fit", "Slim Fit"),
        ("Tight Fit", "Tight Fit"),
    ]
    # Color Choices
    COLOR_CHOICES = [
        ("Khaki", "Khaki"),
        ("Neon", "Neon"),
        ("Printed", "Printed"),
        ("Black", "Black"),
        ("Blue", "Blue"),
        ("Brown", "Brown"),
        ("Burgundy", "Burgundy"),
        ("Green", "Green"),
        ("Grey", "Grey"),
        ("Navy", "Navy"),
        ("Olive", "Olive"),
        ("Orange", "Orange"),
        ("Pink", "Pink"),
        ("Purple", "Purple"),
        ("Red", "Red"),
        ("White", "White"),
        ("Yellow", "Yellow"),
    ]

    # Activity Choices
    ACTIVITY_CHOICES = [
        ("Casual", "Casual"),
        ("Dance", "Dance"),
        ("Golf", "Golf"),
        ("Hiking", "Hiking"),
        ("Running", "Running"),
        ("Tennis", "Tennis"),
        ("Training", "Training"),
        ("Travel", "Travel"),
        ("Work", "Work"),
        ("Workout", "Workout"),
        ("Yoga", "Yoga"),
    ]

    # Fabric Choices
    FABRIC_CHOICES = [
        ("Cotton", "Cotton"),
        ("Fleece", "Fleece"),
        ("Luon", "Luon"),
        ("Mesh", "Mesh"),
        ("Nulu", "Nulu"),
        ("Pima Cotton", "Pima Cotton"),
        ("Ribbed", "Ribbed"),
        ("SenseKnit", "SenseKnit"),
        ("Softstreme", "Softstreme"),
        ("Swift", "Swift"),
        ("Wool", "Wool"),
    ]

    # Product Attributes
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    length = models.CharField(
        max_length=10, choices=LENGTH_CHOICES, blank=True, null=True
    )
    fit = models.CharField(max_length=15, choices=FIT_CHOICES, blank=True, null=True)
    activity = models.CharField(
        max_length=20, choices=ACTIVITY_CHOICES, blank=True, null=True
    )
    fabric = models.CharField(
        max_length=20, choices=FABRIC_CHOICES, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    image1_url = models.URLField(max_length=500, blank=True, null=True)
    image2_url = models.URLField(max_length=500, blank=True, null=True)
    image3_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class PreviousOrders(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name
