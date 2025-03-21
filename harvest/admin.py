from django.contrib import admin
from django import forms
from django.utils.html import format_html
# Register your models here.
from django.contrib import admin
from .models import User, Category, Product, Tag, Article, Order, OrderItem, Review, Event, Inventory, Subscription, Notification,Season
from django.utils.translation import gettext_lazy as _


admin.site.site_header = _("UMP Harverst Administration")
admin.site.site_title = _("UMP Harverst Administration")
admin.site.index_title = _("Growing the future, one harvest at a time.")

# Register the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Register the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}



class ProductAdminForm(forms.ModelForm):
    image_file = forms.FileField(required=False, label="Upload Image")

    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            try:
                upload_result = instance.upload_image_to_server(image_file)
                if not upload_result.get('access_url'):
                    raise Exception("Failed to retrieve the access URL.")
            except Exception as e:
                raise forms.ValidationError(f"Error uploading image: {e}")
        if commit:
            instance.save()
        return instance
    

# Register the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('image_tag','name', 'category', 'price', 'quantity', 'is_featured', 'is_available', 'slug','is_best_selling','review_count')
    search_fields = ('name', 'slug')
    list_filter = ('is_featured', 'is_available', 'category')
    prepopulated_fields = {'slug': ('name',)}
    def image_tag(self, obj):
        if obj.image and obj.image != "leave_blank":
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image)
        return "No Image"

# Register the Tag model
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# Register the Article model
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'is_published', 'slug')
    search_fields = ('title', 'content')
    list_filter = ('is_published', 'author')
    prepopulated_fields = {'slug': ('title',)}

# Register the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')

# Register the OrderItem model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'discount')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order',)

# Register the Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('rating', 'created_at')

# Register the Event model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_active')
    search_fields = ('title', 'location')
    list_filter = ('date', 'is_active')

# Register the Inventory model
# @admin.register(Inventory)
# class InventoryAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity_in_stock', 'restock_date')
#     search_fields = ('product__name',)
#     list_filter = ('restock_date',)

# Register the Subscription model
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'start_date', 'end_date', 'is_active')
    search_fields = ('user__username', 'subscription_type')
    list_filter = ('subscription_type', 'is_active', 'start_date', 'end_date')

# Register the Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'created_at')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')