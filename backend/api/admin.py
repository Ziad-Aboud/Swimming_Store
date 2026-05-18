from django.contrib import admin
from django import forms
from .models import (
    Addresses, Cart, CartItems, Categories, Cities, Coupons, 
    OrderItems, Orders, Payments, PhoneNumbers,  
    ProductCategories, ProductImages, ProductVariants, Products, Reviews, States, 
    Users, Wishlists, UsedCoupons, PaymentMethods
)

class ProductAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Categories.objects.all(),
        required=True,
        widget=admin.widgets.FilteredSelectMultiple('Categories', False),
        help_text='A product must belong to at least one category.'
    )

    class Meta:
        model = Products
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['categories'].initial = Categories.objects.filter(
                productcategories__product=self.instance
            )
            
    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            self._save_categories(product)
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                if old_save_m2m:
                    old_save_m2m()
                self._save_categories(product)
            self.save_m2m = new_save_m2m
        return product

    def _save_categories(self, product):
        selected_categories = self.cleaned_data['categories']
        # Remove unselected
        ProductCategories.objects.filter(product=product).exclude(category__in=selected_categories).delete()
        # Add new ones
        existing = ProductCategories.objects.filter(product=product).values_list('category_id', flat=True)
        for cat in selected_categories:
            if cat.category_id not in existing:
                ProductCategories.objects.create(product=product, category=cat)

class ProductVariantsInline(admin.TabularInline):
    model = ProductVariants
    extra = 0

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 0

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductVariantsInline, ProductImagesInline]
    list_display = ('name', 'base_price', 'is_active')
    search_fields = ('name',)

# Register your models here so they show up in the admin panel
admin.site.register(Addresses)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Categories)
admin.site.register(Cities)
admin.site.register(Coupons)
admin.site.register(OrderItems)
admin.site.register(Orders)
admin.site.register(Payments)
admin.site.register(PhoneNumbers)
admin.site.register(ProductImages)
admin.site.register(ProductVariants)
admin.site.register(Reviews)
admin.site.register(States)
admin.site.register(Users)
admin.site.register(Wishlists)
admin.site.register(UsedCoupons)
admin.site.register(PaymentMethods)
