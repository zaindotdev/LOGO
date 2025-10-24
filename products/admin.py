from django.contrib import admin
from .models import Product, ProductImage, Category

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price','inventory','is_active')
    search_fields = ('title','sku')
    inlines = [ProductImageInline]


admin.site.register(Category)
admin.site.register(ProductImage)