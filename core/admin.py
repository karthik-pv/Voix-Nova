from django.contrib import admin
from django.utils.html import format_html
from .models import Products, Cart, PreviousOrders


class ProductsAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list.html"
    list_display = ("product_image", "name", "price", "category", "gender")

    def product_image(self, obj):
        if obj.image1_url:
            return format_html(
                f'<img src="{obj.image1_url}" style="width: 100px; height: auto;"/>'
            )
        return "No Image"

    product_image.short_description = "Image"


admin.site.register(Products, ProductsAdmin)
admin.site.register(Cart)
admin.site.register(PreviousOrders)
