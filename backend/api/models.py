
from django.db import models


class Addresses(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    street_address = models.CharField(max_length=255)
    city = models.ForeignKey('Cities', models.DO_NOTHING)
    state_province = models.ForeignKey('States', models.DO_NOTHING, db_column='state_province')
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.street_address}, {self.city.name}"

    class Meta:
        db_table = 'addresses'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Cart #{self.cart_id} for {self.user.first_name}"

    class Meta:
        db_table = 'cart'


class CartItems(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, models.DO_NOTHING)
    variant = models.ForeignKey('ProductVariants', models.DO_NOTHING)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.variant.sku} in Cart #{self.cart_id}"

    class Meta:
        db_table = 'cart_items'
        unique_together = (('cart', 'variant'),)


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'


class Cities(models.Model):
    city_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    state = models.ForeignKey('States', models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cities'


class Coupons(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=100)
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.IntegerField(blank=True, null=True)
    times_used = models.IntegerField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.discount_value} {self.discount_type})"

    class Meta:
        db_table = 'coupons'


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    variant = models.ForeignKey('ProductVariants', models.DO_NOTHING)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.variant.sku} in Order #{self.order.order_id}"

    class Meta:
        db_table = 'order_items'
        unique_together = (('order', 'variant'),)


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    address = models.ForeignKey(Addresses, models.DO_NOTHING)
    coupon = models.ForeignKey('Coupons', models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.first_name}"

    class Meta:
        db_table = 'orders'


class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Changed to IntegerField for 0 (Cash) and 1 (Card)
    method = models.IntegerField() 
    status = models.CharField(max_length=50)
    transaction_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.order_id}"

    class Meta:
        db_table = 'payments'


class PhoneNumbers(models.Model):
    # Adding primary_key=True forces Django to stop looking for an 'id' column!
    user = models.OneToOneField('Users', on_delete=models.DO_NOTHING, db_column='user_id', primary_key=True)
    phone_number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.first_name} - {self.phone_number}"

    class Meta:
        db_table = 'phone_numbers'


class ProductCategories(models.Model):
    pk = models.CompositePrimaryKey('product_id', 'category_id')
    product = models.ForeignKey('Products', models.DO_NOTHING)
    category = models.ForeignKey(Categories, models.DO_NOTHING)

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"

    class Meta:
        db_table = 'product_categories'


class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    variant = models.ForeignKey('ProductVariants', models.DO_NOTHING, blank=True, null=True)
    image_url = models.CharField(max_length=500)
    is_primary = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        db_table = 'product_images'


class ProductVariants(models.Model):
    variant_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    sku = models.CharField(unique=True, max_length=100)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.sku} (size: {self.size}, color: {self.color})"

    class Meta:
        db_table = 'product_variants'


class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'


class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rating = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.rating}★ — {self.product.name} by {self.user.first_name}"

    class Meta:
        db_table = 'reviews'
        unique_together = (('user', 'product'),)


class States(models.Model):
    state_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'states'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=255)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        db_table = 'users'


class Wishlists(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    product = models.ForeignKey(Products, models.DO_NOTHING)

    def __str__(self):
        return f"Wishlist: {self.user.first_name} - {self.product.name}"

    class Meta:
        db_table = 'wishlists'
        unique_together = (('user', 'product'),)


class UsedCoupons(models.Model):
    used_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    coupon = models.ForeignKey(Coupons, models.DO_NOTHING)
    
    def __str__(self):
        return f"{self.user.first_name} used {self.coupon.code}"

    class Meta:
        db_table = 'used_coupons'
        # This acts as a UNIQUE constraint, preventing the user from using it twice!
        unique_together = (('user', 'coupon'),)

class PaymentMethods(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField() 
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)
    cvc = models.CharField(max_length=4)
    is_default = models.IntegerField(default=0)

    def __str__(self):
        return f"Card ending in {self.card_number[-4:]}"

    class Meta:
        db_table = 'payment_methods'
