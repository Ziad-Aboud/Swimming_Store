import re

with open("backenddd/api/models.py", "r") as f:
    content = f.read()

# Models and their desired singular names (for verbose_name_plural)
# Since the class is plural, we'll just set verbose_name_plural to the class name as well to stop the double 's'.
models = [
    ("Addresses", "Address", "Addresses", 'return f"{self.street_address}, {self.city.name}, {self.country}"'),
    ("Cart", "Cart", "Carts", 'return f"Cart #{self.cart_id} for {self.user.first_name}"'),
    ("CartItems", "Cart Item", "Cart Items", 'return f"{self.quantity} x {self.variant.product.name} in Cart #{self.cart.cart_id}"'),
    ("Categories", "Category", "Categories", 'return self.name'),
    ("Cities", "City", "Cities", 'return self.name'),
    ("Coupons", "Coupon", "Coupons", 'return f"{self.code} ({self.discount_value} {self.discount_type})"'),
    ("OrderItems", "Order Item", "Order Items", 'return f"{self.quantity} x {self.variant.product.name} in Order #{self.order.order_id}"'),
    ("Orders", "Order", "Orders", 'return f"Order #{self.order_id} by {self.user.first_name}"'),
    ("Payments", "Payment", "Payments", 'return f"Payment #{self.payment_id} (${self.amount}) for Order #{self.order.order_id}"'),
    ("PhoneNumbers", "Phone Number", "Phone Numbers", 'return f"{self.phone_number} (User ID: {self.user.user_id})"'),
    ("ProductImages", "Product Image", "Product Images", 'return f"Image for {self.product.name}"'),
    ("ProductVariants", "Product Variant", "Product Variants", 'return f"{self.product.name} - {self.sku} (size: {self.size}, color: {self.color})"'),
    ("Products", "Product", "Products", 'return self.name'),
    ("Reviews", "Review", "Reviews", 'return f"{self.rating}★ — {self.product.name} by {self.user.first_name}"'),
    ("States", "State", "States", 'return self.name'),
    ("Users", "User", "Users", 'return f"{self.first_name} {self.last_name} ({self.email})"'),
    ("Wishlists", "Wishlist", "Wishlists", 'return f"Wishlist item: {self.product.name} for {self.user.first_name}"'),
    ("UsedCoupons", "Used Coupon", "Used Coupons", 'return f"Coupon {self.coupon.code} used by {self.user.first_name}"'),
    ("PaymentMethods", "Payment Method", "Payment Methods", 'return f"Card ending in {self.card_number[-4:]} (User ID: {self.user_id})"'),
]

for class_name, sg, pl, str_body in models:
    # 1. Inject __str__ if not present
    if f"def __str__(self):" not in content.split(f"class {class_name}(models.Model):")[1].split("class Meta:")[0]:
        pattern = rf"(class {class_name}\(models\.Model\):[\s\S]*?)(    class Meta:)"
        replacement = rf"\1    def __str__(self):\n        {str_body}\n\n\2"
        content = re.sub(pattern, replacement, content, count=1)
    
    # 2. Inject verbose_name_plural if not present
    meta_pattern = rf"(class {class_name}\(models\.Model\):[\s\S]*?class Meta:\n        db_table = '[^']+')(\n|$)"
    if f"verbose_name_plural = '{pl}'" not in content.split(f"class {class_name}(models.Model):")[1]:
        replacement = rf"\1\n        verbose_name_plural = '{pl}'\n"
        content = re.sub(meta_pattern, replacement, content, count=1)

with open("backenddd/api/models.py", "w") as f:
    f.write(content)

print("SUCCESS")
