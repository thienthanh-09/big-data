from django.contrib import admin
from .models import ProductVideo, ProductImage, Category, Product, Store, Order, OrderDetail, Comment, Notification, ProductSale, Profile, Chat, Message, LikedProduct
# Register your models here.

@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'product',)
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'product',)

@admin.register(LikedProduct)
class LikedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'last_modified')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'is_user', 'content', 'image', 'created_at')
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'avatar', 'address', 'phone', 'gender',  'last_access']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'price', 'available', 'sold', 'quantity', 'rating', 'rating_count', 'thumbnail', 'category', 'description']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'store', 'cost', 'status', 'created_at']

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'cost', 'product', 'quantity']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rate', 'content', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at']

@admin.register(ProductSale)
class ProductSalesAdmin(admin.ModelAdmin):
    list_display = ['product', 'value', 'sale_type', 'expired_at', 'created_at']